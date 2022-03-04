# Copyright 2022 Hoshea Jiang
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import time
import copy
import torch
from loguru import logger

from . import utils
from .pointer_model import PointerEncoderDecoder

from .dataset import data
from .dataset.data import Vocab
from .dataset.batcher import Batcher
from .dataset.train_util import get_input_from_batch


class Beam(object):
    def __init__(self, tokens, log_probs, state, context, coverage, ngram_set):
        self.tokens = tokens
        self.log_probs = log_probs
        self.state = state
        self.context = context
        self.coverage = coverage
        self.ngram_set = ngram_set

    def extend(self, token, log_prob, state, context, coverage, new_3gram):
        if self.ngram_set is None:
            ngram_set = None
        else:
            ngram_set = copy.copy(self.ngram_set)
            ngram_set.add(new_3gram)

        return Beam(tokens=self.tokens + [token],
                    log_probs=self.log_probs + [log_prob],
                    state=state,
                    context=context,
                    coverage=coverage,
                    ngram_set=ngram_set)

    def get_new_3gram(self, token):
        new_3gram = tuple(self.tokens[-2:] + [token])
        return new_3gram

    def is_dup_3gram(self, new_3gram):
        if new_3gram in self.ngram_set:
            return True
        return False

    @property
    def latest_token(self):
        return self.tokens[-1]

    @property
    def avg_log_prob(self):
        return sum(self.log_probs) / len(self.tokens)


class BeamSearch(object):
    def __init__(self, params, model_file_path, data_file, ngram_filter=False):
        self.vocab = Vocab(params.vocab_path, params.vocab_size)
        decode_data_path = os.path.join(params.data_dir, data_file)
        self.batcher = Batcher(params, decode_data_path, self.vocab, mode='decode',
                               batch_size=params.beam_size, single_pass=True)
        self.pad_id = self.vocab.word2id(data.PAD_TOKEN)
        assert (self.pad_id == 1)
        time.sleep(10)

        self.model = PointerEncoderDecoder(params, model_file_path, pad_id=self.pad_id, is_eval=True)
        self.params = params

        self.ngram_filter = ngram_filter
        if not self.ngram_filter:
            self.cand_beam_size = self.params.beam_size * 2
        else:
            self.cand_beam_size = self.params.beam_size * 5

    def sort_beams(self, beams):
        return sorted(beams, key=lambda h: h.avg_log_prob, reverse=True)

    def decode(self):
        hyps = []
        batch = self.batcher.next_batch()
        while batch is not None:
            # Run beam search to get best Hypothesis
            best_summary = self.beam_search(batch)

            # Extract the output ids from the hypothesis and convert back to words
            output_ids = [int(t) for t in best_summary.tokens[1:]]
            article_oovs = batch.art_oovs[0] if self.params.pointer_gen else None
            decoded_words = data.outputids2decwords(output_ids, self.vocab, article_oovs, self.params.pointer_gen)

            hyps.append(utils.prepare_rouge_text(" ".join(decoded_words)))

            batch = self.batcher.next_batch()

        return hyps

    def beam_search(self, batch):
        device = torch.device(self.params.eval_device)

        enc_batch, enc_padding_mask, enc_lens, enc_batch_extended, extend_vocab_zeros, c_t_1, coverage_t_0 = \
            get_input_from_batch(self.params, batch, self.params.eval_device)
        c_t_1 = c_t_1.unsqueeze(1)

        enc_outputs, enc_features, s_0 = self.model.encoder(enc_batch, enc_lens)

        dec_h, dec_c = s_0  # 1 x batch_size x 2*hidden_size
        # batch_size x 2*hidden_size
        dec_h = dec_h.squeeze()
        dec_c = dec_c.squeeze()

        # initialize beams
        # TODO: maybe we only need one beam since only beams[0] will be used later at step 0
        beams = [Beam(tokens=[self.vocab.word2id(data.START_DECODING)],
                      log_probs=[0.0],
                      state=(dec_h[0], dec_c[0]),
                      context=c_t_1[0],
                      coverage=(coverage_t_0[0] if self.params.is_coverage else None),
                      ngram_set=set() if self.ngram_filter else None)
                 for _ in range(self.params.beam_size)]
        results = []
        steps = 0
        while steps < self.params.max_dec_steps and len(results) < self.params.beam_size and steps < enc_lens.max():
            latest_tokens = [h.latest_token for h in beams]
            latest_tokens = [t if t < self.vocab.size() else self.vocab.word2id(data.UNKNOWN_TOKEN) \
                             for t in latest_tokens]
            y_t_1 = torch.LongTensor(latest_tokens).to(device)
            all_state_h = []
            all_state_c = []

            all_context = []

            for h in beams:
                state_h, state_c = h.state
                all_state_h.append(state_h)
                all_state_c.append(state_c)

                all_context.append(h.context)

            s_t_1 = (torch.stack(all_state_h, 0).unsqueeze(0), torch.stack(all_state_c, 0).unsqueeze(0))
            c_t_1 = torch.stack(all_context, 0)

            coverage_t = None
            if self.params.is_coverage:
                all_coverage = []
                for h in beams:
                    all_coverage.append(h.coverage)
                coverage_t = torch.stack(all_coverage, 0)

            final_dist, s_t, c_t, attn_dist, coverage_t_plus = self.model.decoder(y_t_1, s_t_1, c_t_1, enc_outputs,
                                                                                  enc_features, enc_padding_mask,
                                                                                  extend_vocab_zeros,
                                                                                  enc_batch_extended, coverage_t)

            log_probs = torch.log(final_dist)
            # for debug
            if torch.isnan(log_probs).any():
                logger.error('log probs contains NAN')

            topk_log_probs, topk_ids = torch.topk(log_probs, self.cand_beam_size)

            dec_h, dec_c = s_t
            dec_h = dec_h.squeeze()
            dec_c = dec_c.squeeze()

            all_beams = []
            num_orig_beams = 1 if steps == 0 else len(beams)
            for i in range(num_orig_beams):
                h = beams[i]
                state_i = (dec_h[i], dec_c[i])
                context_i = c_t[i]
                coverage_i = (coverage_t_plus[i] if self.params.is_coverage else None)

                cur_count = 0
                # we assume that all beam can get no_dup 3-grams in self.cand_beam_size
                for j in range(self.cand_beam_size):  # for each of the top can_beam_size hyps:
                    cur_token = topk_ids[i, j].item()
                    new_3gram = None
                    if self.ngram_filter:
                        new_3gram = h.get_new_3gram(cur_token)
                        if h.is_dup_3gram(new_3gram):
                            continue

                    new_beam = h.extend(token=topk_ids[i, j].item(),
                                        log_prob=topk_log_probs[i, j].item(),
                                        state=state_i,
                                        context=context_i,
                                        coverage=coverage_i,
                                        new_3gram=new_3gram)
                    all_beams.append(new_beam)
                    cur_count += 1
                    if cur_count == self.params.beam_size:
                        break

            if len(all_beams) < 4:
                logger.error(f'Only find {all_beams} candidate beams')

            beams = []
            for h in self.sort_beams(all_beams):
                if h.latest_token == self.vocab.word2id(data.STOP_DECODING):
                    if steps >= self.params.min_dec_steps:
                        results.append(h)
                else:
                    beams.append(h)
                if len(beams) == self.params.beam_size or len(results) == self.params.beam_size:
                    break

            steps += 1

        if len(results) == 0:
            results = beams

        beams_sorted = self.sort_beams(results)

        return beams_sorted[0]
