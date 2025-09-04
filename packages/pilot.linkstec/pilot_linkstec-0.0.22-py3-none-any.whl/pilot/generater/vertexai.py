import re
import threading
from typing import Dict, Any, Optional

import tiktoken
from vertexai.generative_models import GenerativeModel, ChatSession, GenerationConfig
from google.genai import types

class VertexAISingleton:
    _instance: Optional['VertexAISingleton'] = None
    _lock = threading.Lock()
    _tokenizer_cache = {}
    encoding = None

    SQL_SYSTEM_PROMPT_EN = (
        "If there is any SQL-related processing　\n"
        "1. If there is an SQL statement like \"SELECT COUNT(X) INTO :COLUMN FROM TABLE_NAME;\"　please recognize TABLE_NAME as a table."
    )


    def __new__(cls, model_name: str = "gemini-2.5-pro", system_prompt: Optional[str] = None):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(VertexAISingleton, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, model_name: str = "gemini-2.5-pro", system_prompt: Optional[str] = None):
        if not self._initialized:
            with self._lock:
                if not self._initialized:
                    self.model = GenerativeModel(model_name)
                    self.encoding = tiktoken.get_encoding("cl100k_base")
                    # system_promptにSQL_SYSTEM_PROMPT_ENを追加
                    if system_prompt:
                        self.system_prompt = f"{system_prompt.rstrip()}\n\n{self.SQL_SYSTEM_PROMPT_EN}"
                    else:
                        self.system_prompt = self.SQL_SYSTEM_PROMPT_EN
                    self._initialized = True
        else:
            # 既存インスタンスでもsystem_promptを更新可能に
            if system_prompt is not None:
                self.system_prompt = f"{system_prompt.rstrip()}\n\n{self.SQL_SYSTEM_PROMPT_EN}" if system_prompt else self.SQL_SYSTEM_PROMPT_EN

    def generate_content(self, prompt: str) -> Dict[str, Any]:
        """複数スレッドから安全に呼び出し可能"""
        try:
            # システムプロンプトをconfigとして渡す

            generation_config = types.GenerateContentConfig(
                system_instruction = self.system_prompt
            )
            prompt = self.exchange_prompt(prompt)
            response = self.model.generate_content(
                contents=prompt,  # 引数名を明示
                generation_config = generation_config  # 正しい名前で渡す
            )
            return {
                "prompt": prompt,
                "response": self._remove_code_fence(response.text),
                "success": True,
                "error": None
            }
        except Exception as e:
            return {
                "prompt": prompt,
                "response": None,
                "success": False,
                "error": str(e)
            }

    def start_chat(self) -> ChatSession:
        """新しいチャットセッションを開始"""
        return self.model.start_chat()

    def count_tokens(self, text: str) -> int:
        """与えられたテキストのトークン数を返す（bert-base-uncasedのみ使用）"""
        try:
            tokens = self.encoding.encode(text)
            return len(tokens)
        except Exception as e:
            print(f"トークン計算失敗: {e}")
            return 0

    def _remove_code_fence(self, text: str) -> str:
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        return "\n".join(lines)


    def exchange_prompt(self, prompt: str) -> str:
        # EXEC SQL ... END-EXEC. のSQL部分を抽出してフラット化
        rtn_prompt = self.fix_initialize(prompt)
        rtn_prompt = self.extract_and_flatten_sql(rtn_prompt)
        return rtn_prompt

    def fix_initialize(self, text: str) -> str:
        # SECTION ... EXIT. ブロック内のINITIALIZE文を処理
        def process_section_block(match):
            section_content = match.group(0)

            # INITIALIZE の行を結合する（SECTION-EXIT間のみ）
            # INITIALIZEで始まる行の次の行が空白+文字列の場合に結合
            pattern_init = r'^(\s*INITIALIZE\s+[^\n]*)\n(\s+[^\n]+(?:\s+[^\n]+)*)'

            def repl_init(m):
                init_line = m.group(1).rstrip()
                next_lines = m.group(2).strip()
                return f'{init_line} {next_lines}'

            section_content = re.sub(pattern_init, repl_init, section_content, flags=re.MULTILINE)

            # ブロック内　COUNT(*) → COUNT(1) へ置換する
            section_content = re.sub(r'COUNT\(\s*\*\s*\)', 'COUNT(1)', section_content, flags=re.IGNORECASE)

            return section_content

        # SECTION から EXIT. までのブロックを検索して処理
        section_pattern = r'(\w+\s+SECTION\s*\..*?EXIT\s*\.)'
        text = re.sub(section_pattern, process_section_block, text, flags=re.DOTALL | re.IGNORECASE)

        return text


    def extract_and_flatten_sql(self, code):
        # EXEC SQL ... END-EXEC. にマッチ
        pattern = r"EXEC SQL(.*?)END-EXEC\.?"

        def repl(m):
            # .*?でSQL部分取得
            raw_sql = m.group(1)
            # コメント（*以降）除去（複数行まとめてOK）
            no_comment = re.sub(r"\*.*", "", raw_sql)
            # 改行/連続スペースを単一スペースに
            flattened = re.sub(r"\s+", " ", no_comment).strip()
            # 置換内容
            return f"EXEC SQL {flattened} END-EXEC."

        # 全て置換
        result = re.sub(pattern, repl, code, flags=re.DOTALL | re.IGNORECASE)
        return result


    @classmethod
    def get_instance(cls, model_name: str = "gemini-2.5-pro", system_prompt: Optional[str] = None) -> 'VertexAISingleton':
        """インスタンスを取得"""
        return cls(model_name, system_prompt)
