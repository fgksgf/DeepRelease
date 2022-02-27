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

import re

FILENAMES = [
    'PULL_REQUEST_TEMPLATE.md',
    'pull_request_template.md',
    'PULL_REQUEST_TEMPLATE',
]

GITHUB_CONTENT_URL = 'https://raw.githubusercontent.com/{owner}/{repo}/master/.github/{filename}'


def get_template_content(owner: str, repo: str) -> str:
    """
    获取GitHub项目的PR模板内容
    :param owner:
    :param repo:
    :return:
    """
    content = None
    for filename in FILENAMES:
        try:
            url = f'https://raw.githubusercontent.com/{owner}/{repo}/master/.github/{filename}'
            resp = requests.get(url, headers=Constants.HEADERS)
            resp.raise_for_status()
            content = str(resp.content.decode("utf-8"))
            break
        except Exception:
            continue

    if not content:
        return ''
    return content


def re_strip(string, char=r"\W"):
    result = re.sub(f"^{char}+", "", string)
    result = re.sub(f"{char}+$", "", result)
    return result


def remove_template(fn: str):
    df = pd.read_csv(fn)

    # 删除title列值为空的行（表示该行无PR数据）
    df['title'].replace('', np.nan, inplace=True)
    df.dropna(axis=0, subset=['title'], inplace=True)
    print(fn, '删除无PR数据的行后: ', df.shape)

    d = parse_url(str(df.iloc[1, 2]))
    template = get_template_content(d.get('owner'), d.get('name'))
    if template != '':
        df['desc'] = df['desc'].apply(remove_str, args=(template,))

    df.to_csv(f'{fn}-rm-tmpl.csv', index=False, quoting=1)
    # else:
    #     df.to_csv(f'{fn}', index=False, quoting=1)


def remove_str(s: str, t: str) -> str:
    s = str(s)
    if len(s) == 0:
        return s
    for i in t.split('\n'):
        tmp = re_strip(i).strip()
        if len(tmp) > 0:
            s = s.replace(tmp, '')
    return s