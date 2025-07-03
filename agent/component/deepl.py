from abc import ABC
from agent.component.base import ComponentBase, ComponentParamBase
import deepl


class DeepLParam(ComponentParamBase):
    """
    Define the DeepL component parameters.
    """

    def __init__(self):
        super().__init__()
        self.auth_key = "xxx"
        self.parameters = []
        self.source_lang = 'ZH'
        self.target_lang = 'EN-GB'

    def check(self):
        self.check_positive_integer(self.top_n, "Top N")
        self.check_valid_value(self.source_lang, "Source language",
                               ['AR', 'BG', 'CS', 'DA', 'DE', 'EL', 'EN', 'ES', 'ET', 'FI', 'FR', 'HU', 'ID', 'IT',
                                'JA', 'KO', 'LT', 'LV', 'NB', 'NL', 'PL', 'PT', 'RO', 'RU', 'SK', 'SL', 'SV', 'TR',
                                'UK', 'ZH'])
        self.check_valid_value(self.target_lang, "Target language",
                               ['AR', 'BG', 'CS', 'DA', 'DE', 'EL', 'EN-GB', 'EN-US', 'ES', 'ET', 'FI', 'FR', 'HU',
                                'ID', 'IT', 'JA', 'KO', 'LT', 'LV', 'NB', 'NL', 'PL', 'PT-BR', 'PT-PT', 'RO', 'RU',
                                'SK', 'SL', 'SV', 'TR', 'UK', 'ZH'])


class DeepL(ComponentBase, ABC):
    component_name = "GitHub"

    def _run(self, history, **kwargs):
        ans = self.get_input()
        ans = " - ".join(ans["content"]) if "content" in ans else ""
        if not ans:
            return DeepL.be_output("")

        try:
            translator = deepl.Translator(self._param.auth_key)
            result = translator.translate_text(ans, source_lang=self._param.source_lang,
                                               target_lang=self._param.target_lang)

            return DeepL.be_output(result.text)
        except Exception as e:
            DeepL.be_output("**Error**:" + str(e))
