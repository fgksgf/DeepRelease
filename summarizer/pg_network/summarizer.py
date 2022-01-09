# Copyright 2021 Hoshea Jiang
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

from summarizer.base import Summarizer
from summarizer.pg_network import utils
from summarizer.pg_network.dataset import data, batcher
from summarizer.pg_network.dataset.train_util import get_input_from_batch
from summarizer.pg_network.decode import BeamSearch


class EntrySummarizer(Summarizer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def summarize(self, items):
        pass

    def preprocess(self, items):
        pass

    @staticmethod
    def decode(param_path, model_path, ngram_filter, data_file_prefix="test."):
        params = utils.Params(param_path)
        decode_processor = BeamSearch(params, model_path, data_file_prefix=data_file_prefix, ngram_filter=ngram_filter)
        decode_processor.decode()


class Procedure:
    """Base class of all process-related classes in order to share similar process"""

    def __init__(self, params, is_eval=False):
        self.vocab = data.Vocab(params.vocab_path, params.vocab_size)
        train_data_path = os.path.join(params.data_dir, "train." + params.data_file_suffix)
        eval_data_path = os.path.join(params.data_dir, "valid." + params.data_file_suffix)
        if not is_eval:
            self.batcher = batcher.Batcher(params, train_data_path, self.vocab, mode='train',
                                           batch_size=params.batch_size, single_pass=False)
        else:
            self.batcher = batcher.Batcher(params, eval_data_path, self.vocab, mode='eval',
                                           batch_size=params.batch_size, single_pass=True)
        self.pad_id = self.vocab.word2id(data.PAD_TOKEN)
        self.end_id = self.vocab.word2id(data.STOP_DECODING)
        self.unk_id = self.vocab.word2id(data.UNKNOWN_TOKEN)
        assert (self.pad_id == 1)
        self.dump_dir = None
        self.params = params
        self.is_eval = is_eval

    def infer_one_batch(self, batch, iter=None, is_eval=False):
        if is_eval:
            device = self.params.eval_device
        else:
            device = self.params.device
        device = torch.device(device)
        train_ml = getattr(self.params, "train_ml", True)
        train_rl = getattr(self.params, "train_rl", False)

        # c_t_1: batch_size x 2*hidden_dim
        enc_batch, enc_padding_mask, enc_lens, enc_batch_extended, extend_vocab_zeros, c_t_1, coverage_0 = \
            get_input_from_batch(self.params, batch, device)
        # get encoder_output
        enc_outputs, enc_features, s_0 = self.model.encoder(enc_batch, enc_lens)

        enc_package = [s_0, c_t_1, coverage_0, enc_outputs, enc_features, enc_padding_mask, extend_vocab_zeros,
                       enc_batch_extended]

        if train_ml:
            ml_loss = self.infer_one_batch_ml(batch, *enc_package, iter, device=device)
        else:
            ml_loss = torch.tensor(0.0, dtype=torch.float, device=device)

        if train_rl:
            rl_loss, reward = self.infer_one_batch_rl(batch, *enc_package, iter, device=device)
        else:
            rl_loss = torch.tensor(0.0, dtype=torch.float, device=device)
            reward = torch.tensor(0.0, dtype=torch.float, device=device)

        rl_weight = getattr(self.params, "rl_weight", 0.0)
        loss = rl_weight * rl_loss + (1 - rl_weight) * ml_loss

        if not is_eval:
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

        return loss.item(), reward.item()

    def infer_one_batch_ml(self, batch, s_0, c_t_1, coverage_0, enc_outputs, enc_features, enc_padding_mask,
                           extend_vocab_zeros, enc_batch_extended, iter, device):
        dec_batch, dec_padding_mask, max_dec_len, dec_lens_var, target_batch = \
            get_output_from_batch(self.params, batch, device)

        s_t_1 = s_0
        c_t_1 = c_t_1.unsqueeze(1)
        coverage_t = coverage_0

        teacher_forcing_ratio = getattr(self.params, "teacher_forcing_ratio", 1.0)
        teacher_forcing = True if random.random() < teacher_forcing_ratio else False
        step_losses = []
        for di in range(min(max_dec_len, self.params.max_dec_steps)):
            if di == 0 or teacher_forcing:
                y_t_1 = dec_batch[:, di]
            else:
                y_t_1 = y_t
            # first we have coverage_t_1, then we have a_t
            final_dist, s_t_1, c_t_1, attn_dist, coverage_t_plus = self.model.decoder(y_t_1, s_t_1, c_t_1, enc_outputs,
                                                                                      enc_features, enc_padding_mask,
                                                                                      extend_vocab_zeros,
                                                                                      enc_batch_extended, coverage_t)
            # if pointer_gen is True, the target will use the extend_vocab
            target = target_batch[:, di]
            # batch
            y_t = final_dist.max(1)[1]
            # batch x extend_vocab_size -> batch x 1 -> batch
            gold_probs = torch.gather(final_dist, 1, target.unsqueeze(1)).squeeze()
            step_loss = -torch.log(gold_probs + self.params.eps)

            if self.params.is_coverage:
                # batch
                step_coverage_loss = torch.sum(torch.min(attn_dist, coverage_t), dim=1)
                step_loss = step_loss + self.params.cov_loss_wt * step_coverage_loss
                coverage_t = coverage_t_plus

            step_mask = dec_padding_mask[:, di]
            step_loss = step_loss * step_mask
            step_losses.append(step_loss)

        sum_losses = torch.sum(torch.stack(step_losses, 1), 1)
        batch_avg_loss = sum_losses / dec_lens_var

        loss = torch.mean(batch_avg_loss)

        return loss

    def infer_one_batch_rl(self, batch, s_0, c_t_1, coverage_0, enc_outputs, enc_features, enc_padding_mask,
                           extend_vocab_zeros, enc_batch_extended, iter, device):
        if self.params.is_coverage == True:
            raise ValueError("do not support training rl loss with coverage now")

        s_t_1 = s_0
        c_t_1 = c_t_1.unsqueeze(1)
        coverage_t = coverage_0

        # decode one batch
        decode_input = [batch, s_t_1, c_t_1, enc_outputs, enc_features, enc_padding_mask, extend_vocab_zeros,
                        enc_batch_extended, coverage_t, device]
        sample_seqs, rl_log_probs = self.decode_one_batch_rl(False, *decode_input)
        with torch.autograd.no_grad():
            baseline_seqs, _ = self.decode_one_batch_rl(True, *decode_input)

        sample_reward = reward_function(sample_seqs, batch.original_abstracts, device=device)
        baseline_reward = reward_function(baseline_seqs, batch.original_abstracts, device=device)
        rl_loss = -(sample_reward - baseline_reward) * rl_log_probs
        rl_loss = torch.mean(rl_loss)
        batch_reward = torch.mean(sample_reward)

        return rl_loss, batch_reward

    def decode_one_batch_rl(self, greedy, batch, s_t_1, c_t_1, enc_outputs, enc_features, enc_padding_mask,
                            extend_vocab_zeros, enc_batch_extended, coverage_t, device):
        # No teacher forcing for RL
        dec_batch, _, max_dec_len, dec_lens_var, target_batch = get_output_from_batch(self.params, batch, device)
        log_probs = []
        decode_ids = []
        # we create the dec_padding_mask at the runtime
        dec_padding_mask = []
        y_t = dec_batch[:, 0]
        mask_t = torch.ones(len(enc_outputs), dtype=torch.long, device=device)
        # there is at least one token in the decoded seqs, which is STOP_DECODING
        for di in range(min(max_dec_len, self.params.max_dec_steps)):
            y_t_1 = y_t
            # first we have coverage_t_1, then we have a_t
            final_dist, s_t_1, c_t_1, attn_dist, coverage_t_plus = self.model.decoder(y_t_1, s_t_1, c_t_1, enc_outputs,
                                                                                      enc_features, enc_padding_mask,
                                                                                      extend_vocab_zeros,
                                                                                      enc_batch_extended, coverage_t)
            if not greedy:
                # sampling
                multi_dist = Categorical(final_dist)
                y_t = multi_dist.sample()
                log_prob = multi_dist.log_prob(y_t)
                log_probs.append(log_prob)

                y_t = y_t.detach()
                dec_padding_mask.append(mask_t.detach().clone())
                mask_t[(mask_t == 1) + (y_t == self.end_id) == 2] = 0
            else:
                # baseline
                y_t = final_dist.max(1)[1]
                y_t = y_t.detach()

            decode_ids.append(y_t)
            # for next input
            is_oov = (y_t >= self.vocab.size()).long()
            y_t = (1 - is_oov) * y_t + is_oov * self.unk_id

        decode_ids = torch.stack(decode_ids, 1)

        if not greedy:
            dec_padding_mask = torch.stack(dec_padding_mask, 1).float()
            log_probs = torch.stack(log_probs, 1) * dec_padding_mask
            dec_lens = dec_padding_mask.sum(1)
            log_probs = log_probs.sum(1) / dec_lens
            if (dec_lens == 0).any():
                print("Decode lengths encounter zero!")
                print(dec_lens)

        decoded_seqs = []
        for i in range(len(enc_outputs)):
            dec_ids = decode_ids[i].cpu().numpy()
            article_oovs = batch.art_oovs[i]
            dec_words = data.outputids2decwords(dec_ids, self.vocab, article_oovs,
                                                self.params.pointer_gen)
            if len(dec_words) < 2:
                dec_seq = "xxx"
            else:
                dec_seq = " ".join(dec_words)
            decoded_seqs.append(dec_seq)

        return decoded_seqs, log_probs
