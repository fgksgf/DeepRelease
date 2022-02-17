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

import numpy as np
import torch


def get_input_from_batch(params, batch, device):
    device = torch.device(device)
    batch_size = len(batch.enc_lens)

    enc_batch = torch.from_numpy(batch.enc_batch).long().to(device)
    enc_padding_mask = torch.from_numpy(batch.enc_padding_mask).float().to(device)
    enc_lens = batch.enc_lens
    extra_zeros = None
    enc_batch_extend_vocab = None

    if params.pointer_gen:
        enc_batch_extend_vocab = torch.from_numpy(batch.enc_batch_extend_vocab).long().to(device)
        # max_art_oovs is the max over all the article oov list in the batch
        if batch.max_art_oovs > 0:
            extra_zeros = torch.zeros((batch_size, batch.max_art_oovs)).to(device)

    c_t_1 = torch.zeros((batch_size, 2 * params.hidden_dim)).to(device)

    coverage = None
    if params.is_coverage:
        coverage = torch.zeros(enc_batch.size()).to(device)

    return enc_batch, enc_padding_mask, enc_lens, enc_batch_extend_vocab, extra_zeros, c_t_1, coverage


def get_output_from_batch(params, batch, device):
    device = torch.device(device)
    dec_batch = torch.from_numpy(batch.dec_batch).long().to(device)
    dec_padding_mask = torch.from_numpy(batch.dec_padding_mask).float().to(device)
    dec_lens = batch.dec_lens
    max_dec_len = np.max(dec_lens)
    dec_lens_var = torch.from_numpy(dec_lens).float().to(device)

    target_batch = torch.from_numpy(batch.target_batch).long().to(device)

    return dec_batch, dec_padding_mask, max_dec_len, dec_lens_var, target_batch
