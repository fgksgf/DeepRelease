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

PARAMS = {
    "data_dir": "summarizer/pg_network/data",
    "hidden_dim": 256,
    "embed_dim": 128,
    "batch_size": 8,
    "max_enc_steps": 400,
    "max_dec_steps": 100,
    "beam_size": 4,
    "min_dec_steps": 3,
    "vocab_size": 30000,
    "eps": 1e-12,
    "max_iterations": 40000,
    "optim": "Adam",
    "lr": 0.0001,
    "reoptim": True,
    "teacher_forcing_ratio": 1,
    "pointer_gen": True,
    "is_coverage": False,
    "lr_coverage": 0.15,
    "cov_loss_wt": 1.0,
    "train_ml": True,
    "train_rl": True,
    "rl_weight": 0.9984,
    "device": "cpu",
    "eval_device": "cpu",
    "summary_flush_interval": 100,
    "print_interval": 200,
    "eval_print_interval": 1000,
    "test_print_interval": 1000,
    "save_interval": 1000
}


class Params:
    def __init__(self):
        self.__dict__.update(PARAMS)

    @property
    def dict(self):
        """Gives dict-like access to Params instance by `params.dict['learning_rate']"""
        return self.__dict__
