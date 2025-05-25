import asyncio
import os
import uuid

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.func import entrypoint, task
from langgraph.graph import END, StateGraph
from langgraph.graph.graph import CompiledGraph
from langgraph.types import interrupt

from agents.biz_requirement.schemas import (
    DetailedSectionContent,
    DynamicOutline,
    ProjectBusinessRequirement,
    RequirementDocument,
    RequirementsPhase,
    RequirementState,
)
from agents.core.agent_builder import AgentGraphBuilder

# 必須項目と任意項目を分ける
MANDATORY = [
    'project_name',
    'background',
    'goals',
    'stake_holders',
    'scopes',
]

OPTIONAL = [
    'constraints',
    'non_functional',
    'budget',
    'schedule',
    'assumptions',  # 新たに追加
    'risks',  # 新たに追加
    'compliance',  # 新たに追加
]

# 質問テンプレートを非技術者向けに修正
QUESTION_TEMPLATES = {
    'project_name': 'このプロジェクト・システム開発の名前は何ですか？まだ決まっていなければ仮の名前でも構いません。',
    'background': 'このプロジェクトを始めようと思った理由や、現在抱えている問題を教えてください。',
    'goals': 'このプロジェクトで達成したいことは何ですか？成功と言えるためには、どのような結果が必要ですか？',
    'stake_holders': 'このプロジェクトに関わる人や部署・会社を教えてください。例えば「営業部」「エンドユーザー」「IT部門」など。',
    'scopes': 'このプロジェクトで作るもの・含めるものと、含めないものを教えてください。',
    'constraints': '予算の上限や、守るべきルール、技術的な制約などはありますか？',
    'non_functional': 'システムの速さ、セキュリティ、使いやすさなどについて、特に重視する点はありますか？',
    'budget': 'このプロジェクトの予算はどのくらいでしょうか？目安でも構いません。',
    'schedule': 'いつ頃始めて、いつ頃完成させたいですか？重要な節目があれば教えてください。',
    'assumptions': 'このプロジェクトを進める上での前提条件（例：「すでに〇〇のデータがある」など）はありますか？',
    'risks': '心配している課題やリスクがあれば教えてください。',
    'compliance': '特に守るべき法律やルールはありますか？',
}

# 専門用語の説明
TERM_EXPLANATIONS = {
    'KPI': '目標の達成度を測るための指標のことです。例えば「売上20%増加」「顧客満足度80%以上」などです。',
    'ステークホルダー': 'プロジェクトに関わる人や組織のことです。例えば「お客様」「開発チーム」「営業部門」などです。',
    '法規制': '守るべき法律や規則のことです。例えば「個人情報保護法」「業界ガイドライン」などです。',
    '非機能要件': 'システムの動作以外の特性のことです。例えば「応答速度」「セキュリティ対策」「使いやすさ」などです。',
    'スコープ': 'プロジェクトで実現する範囲と、含まないものを明確にすることです。',
    'マイルストーン': 'プロジェクトの重要な節目や達成すべき中間目標のことです。',
}
GOOGLE_GENAI_MODEL = 'models/gemini-1.5-pro'

llm = ChatGoogleGenerativeAI(model=GOOGLE_GENAI_MODEL, temperature=0.7)
check_pointer = InMemorySaver()
config = {'configurable': {'thread_id': uuid.uuid4()}}


class BizRequirementAgent(AgentGraphBuilder):
    def __init__(self):
        super().__init__(state_object=RequirementState)

    def build_graph(self) -> CompiledGraph:
        """要件定義書作成のワークフローグラフを構築する"""
        # ノードの追加
        self.workflow.add_node('intro', self._introduction_node)
        self.workflow.add_node('followup', self._followup_node)
        self.workflow.add_node('help', self._help_node)
        self.workflow.add_node('outline_generation', self._outline_generation_node)
        self.workflow.add_node('detail_generation', self._detail_generation_node)
        self.workflow.add_node('document_integration', self._document_integration_node)

        # 条件付きエントリポイント設定
        self.workflow.set_conditional_entry_point(
            self._decide_entry_point,
            {
                'intro': 'intro',
                'followup': 'followup',
                'help': 'help',
            },
        )

        # エッジの設定
        self.workflow.add_edge('intro', 'followup')
        self.workflow.add_conditional_edges(
            'followup',
            self._decide_next_from_followup,
            {
                'outline_generation': 'outline_generation',
                'followup': 'followup',
                'help': 'help',
            },
        )
        self.workflow.add_conditional_edges(
            'help',
            self._decide_next_from_help,
            {
                'followup': 'followup',
            },
        )
        self.workflow.add_edge('outline_generation', 'detail_generation')
        self.workflow.add_edge('detail_generation', 'document_integration')
        self.workflow.add_edge('document_integration', END)

        return self.workflow.compile(checkpointer=check_pointer)

    def _decide_entry_point(self, state: RequirementState):
        """エントリーポイントを決定する"""
        if state.get('user_wants_help'):
            return 'help'
        elif state.get('current_phase') and state['current_phase'] != RequirementsPhase.INTRODUCTION:
            return 'followup'
        return 'intro'

    def _decide_next_from_followup(self, state: RequirementState):
        """フォローアップノードからの次の遷移先を決定する"""
        if state.get('user_wants_help'):
            return 'help'
        elif state.get('interview_complete') and state.get('current_phase') == RequirementsPhase.OUTLINE_GENERATION:
            return 'outline_generation'
        return 'followup'

    def _decide_next_from_help(self, state: RequirementState):
        """ヘルプノードからの次の遷移先を決定する"""
        return 'followup'

    def _introduction_node(self, state: RequirementState) -> RequirementState:
        """初期の導入メッセージを提供するノード"""
        state['current_phase'] = RequirementsPhase.INTRODUCTION
        mandatory_list = '\n'.join([f'- {QUESTION_TEMPLATES[key]}' for key in MANDATORY])

        introduction_message_content = f"""こんにちは！私は要求定義ドキュメント作成をサポートするアシスタントです。
これからプロジェクトの背景や目的などについてお伺いしていきます。

主に以下の項目について教えていただければと思います：
{mandatory_list}

わからない項目があっても大丈夫です。その場合は「わからない」とお伝えください。
私が他の情報から推測してみます。また、途中で「ヘルプ」とおっしゃっていただければ、専門用語の説明をいたします。

まずは、プロジェクトについて自由に教えていただけますか？
"""
        updated_messages = state.get('messages', []) + [AIMessage(content=introduction_message_content)]
        return {
            'messages': updated_messages,
            'current_phase': RequirementsPhase.INTERVIEW,
            'asked_for_optional': False,
            'technical_level': 'beginner',  # デフォルトは初心者レベルと仮定
            'skipped_questions': [],
        }

    def _help_node(self, state: RequirementState) -> RequirementState:
        """専門用語の説明を提供するノード"""
        term_explanations = '\n'.join([f'・{term}： {explanation}' for term, explanation in TERM_EXPLANATIONS.items()])

        help_message_content = f"""【専門用語の説明】
{term_explanations}

他にご質問があればお気軽にどうぞ。引き続き、プロジェクトについて教えていただければと思います。
"""
        updated_messages = state.get('messages', []) + [AIMessage(content=help_message_content)]
        return {
            'messages': updated_messages,
            'user_wants_help': False,  # ヘルプを提供したのでフラグをリセット
        }

    def _followup_node(self, state: RequirementState) -> RequirementState:
        """ユーザー入力に基づいて要件情報を更新し、次のアクションを決定するノード"""
        user_message = self._get_last_user_message(state)
        if not user_message:
            user_message = interrupt('ユーザの入力を待っています。')
            updated_mesage = state.get('messages', []) + [HumanMessage(content=user_message)]
            return {
                'messages': updated_mesage,
            }

        # 特殊コマンドの処理
        special_command_result = self._handle_special_commands(state, user_message)
        if special_command_result:
            return special_command_result

        # 通常の入力処理：要件情報の更新
        current_requirement = self._update_requirements(state, user_message)
        updated_state = self._handle_updated_requirement_state(current_requirement=current_requirement, state=state)
        return updated_state

    def _outline_generation_node(self, state: RequirementState) -> RequirementState:
        """要求定義書のアウトラインを生成するノード"""
        print('要求定義ドキュメントのアウトラインを動的に生成します...')
        requirement = state.get('requirement')
        if not requirement:
            err_msg = 'エラー: アウトライン生成のための要求情報がありません。ヒアリングに戻ります。'
            return {
                'messages': state.get('messages', []) + [AIMessage(content=err_msg)],
                'current_phase': RequirementsPhase.INTERVIEW,
                'interview_complete': False,
            }

        # アウトライン生成のコード
        outline_system_msg = """あなたは経験豊富なプロジェクトマネージャーであり、優れたドキュメント作成の専門家です。
提供されたプロジェクト情報に基づいて、読者にとって最も理解しやすく論理的な要求定義書の「章立て」と「各章の主要な見出し」を提案してください。

考慮すべき点:
- プロジェクトの目的と背景が明確に伝わる構成になっているか？
- 主要なステークホルダーとその期待が整理されているか？
- プロジェクトの範囲、制約、リスクが明確になっているか？
- 提供された情報の中で特に重要な点や、このプロジェクト特有の注目すべき点は何か？それらを効果的に組み込むにはどうすればよいか？
- 一般的な要求定義書の構成要素（例：概要、目的、スコープ、ステークホルダー、制約、リスクなど）を参考にしつつも、提供された情報に基づいて最適な順序と粒度になっているか？"""

        outline_user_msg = """思考プロセス（Chain of Thought）:
どのような思考プロセスでそのアウトライン構造に至ったのか、具体的な理由や判断基準も合わせて説明してください。

プロジェクト情報:
{project_info}

出力形式の指示に従い、JSONオブジェクトで結果を返してください:
{format_instructions}
"""
        prompt = ChatPromptTemplate.from_messages([('system', outline_system_msg), ('human', outline_user_msg)])
        requirement_json = state['requirement'].model_dump_json(indent=2, exclude_none=True)
        parser = PydanticOutputParser(pydantic_object=DynamicOutline)
        chain = prompt | llm | parser
        outline_result: DynamicOutline = chain.invoke(
            {
                'project_info': requirement_json,
                'format_instructions': parser.get_format_instructions(),
            }
        )
        return {
            'messages': state.get('messages', []) + [AIMessage(content='アウトラインを生成しました。次に詳細を記述します。')],
            'dynamic_outline': outline_result,
            'current_phase': RequirementsPhase.DETAIL_GENERATION,
        }

    async def _detail_generation_node(self, state: RequirementState) -> RequirementState:
        """要求定義書の詳細を生成するノード"""
        print('要求定義ドキュメントの詳細を動的に生成します...')
        dynamic_outline = state.get('dynamic_outline')
        # アウトラインが生成されているか確認
        if not dynamic_outline:
            err_msg = 'エラー: アウトラインが生成されていません。アウトライン生成に戻ります。'
            return {
                'messages': state.get('messages', []) + [AIMessage(content=err_msg)],
                'current_phase': RequirementsPhase.OUTLINE_GENERATION,
            }

        # 要件情報が存在するか確認
        requirement = state.get('requirement')
        if not requirement:
            err_msg = 'エラー: 詳細生成のための要求情報がありません。ヒアリングに戻ります。'
            return {
                'messages': state.get('messages', []) + [AIMessage(content=err_msg)],
                'current_phase': RequirementsPhase.INTERVIEW,
                'interview_complete': False,
            }

        detailed_sections = []
        futures = []
        task_mapping = {}

        for section in dynamic_outline.suggested_outline:
            generation_task = self._detail_generation_task(
                requirement=requirement,
                dynamic_outline=dynamic_outline,
                section_title=section.section_title,
                heading=None,
            )
            section_future = asyncio.create_task(generation_task)
            futures.append(section_future)
            task_mapping[section_future.get_name()] = ('section', section.section_title, None)

            for heading in section.headings:
                heading_task = self._detail_generation_task(
                    requirement=requirement,
                    dynamic_outline=dynamic_outline,
                    section_title=section.section_title,
                    heading=heading,
                )
                heading_future = asyncio.create_task(heading_task)
                futures.append(heading_future)
                task_mapping[heading_future.get_name()] = ('heading', section.section_title, heading)

        results = await asyncio.gather(*futures)

        for result in results:
            section_type, section_title, heading = task_mapping[result.get_name()]
            if section_type == 'heading':
                if isinstance(result, list) and len(result) > 0:
                    detailed_content = result[0]
                else:
                    detailed_content = result
            else:
                detailed_content = result

            detailed_sections.append(detailed_content)

        return {
            'messages': state.get('messages', [])
            + [AIMessage(content='各セクションの詳細内容を生成しました。最終ドキュメントを統合します。')],
            'detailed_sections': detailed_sections,
            'current_phase': RequirementsPhase.DOCUMENT_INTEGRATION,
        }

    def _document_integration_node(self, state: RequirementState) -> RequirementState:
        """要求定義書をドキュメントツールに統合するノード"""
        print('要求定義ドキュメントをドキュメントツールに統合します...')
        detailed_sections = state.get('detailed_sections', [])
        requirement = state.get('requirement')
        if not detailed_sections:
            err_msg = 'エラー: 詳細セクションが生成されていません。詳細生成に戻ります。'
            return {
                'messages': state.get('messages', []) + [AIMessage(content=err_msg)],
                'current_phase': RequirementsPhase.DETAIL_GENERATION,
            }

        integration_system_msg = """あなたは経験豊富なテクニカルライターです。
提供された各セクションのマークダウンコンテンツを統合して、一貫性のある完全な要求定義書を作成してください。

考慮すべき点:
- 全体的な一貫性と流れを確保する
- 重複する内容を適切に整理する
- セクション間のスムーズな遷移を確保する
- 適切な目次と見出しレベルを設定する
- マークダウンの書式を正確に適用する
- 専門用語の使用に一貫性を持たせる"""

        integration_user_msg = """以下の詳細セクションを統合して、完全な要求定義書を作成してください:

プロジェクト名: {project_name}

セクション詳細:
{detailed_sections}

整合性と流れに注意し、マークダウン形式で最終ドキュメントを作成してください。
ドキュメントの先頭には適切な見出しとプロジェクト名を含めてください。

出力形式の指示に従い、JSONオブジェクトで結果を返してください:
{format_instructions}
"""
        parser = PydanticOutputParser(pydantic_object=RequirementDocument)
        intergration_prompt = ChatPromptTemplate.from_messages(
            [('system', integration_system_msg), ('human', integration_user_msg)]
        ).partial(format_instructions=parser.get_format_instructions())

        detailed_sections_text = '\n\n'.join(
            [
                f'## {section.section_title}'
                + (f'\n### {section.heading}' if section.heading else '')
                + f'\n{section.markdown_content}'
                for section in state.get('detailed_sections', [])
            ]
        )
        project_name = requirement.project_name or 'プロジェクト名未設定'
        final_markdown = intergration_prompt | llm | parser
        final_document: RequirementDocument = final_markdown.invoke(
            {'project_name': project_name, 'detailed_sections': detailed_sections_text}
        )
        if not final_document:
            err_msg = 'エラー: ドキュメントの統合に失敗しました。'
            return {
                'messages': state.get('messages', []) + [AIMessage(content=err_msg)],
                'current_phase': RequirementsPhase.DOCUMENT_INTEGRATION,
            }

        file_path = f'outputs/{project_name.replace(" ", "_")}_biz_requirement.md'
        self._saved_document(final_document, file_path)
        completion_message = f"""
要求定義書の作成が完了しました！

プロジェクト名: {project_name}

ファイルパス: {file_path}

ご質問や修正が必要な点がありましたら、お気軽にお申し付けください。
"""
        return {
            'messages': state.get('messages', []) + [AIMessage(content=completion_message)],
            'document': final_document,
            'current_phase': END,
        }

    async def _detail_generation_task(
        self,
        requirement: ProjectBusinessRequirement,
        dynamic_outline: DynamicOutline,
        section_title: str,
        heading: str | None,
    ):
        """セクションやヘッディングの詳細内容を生成するタスク"""
        detail_system_msg = """あなたは経験豊富なプロジェクトマネージャーで、要求定義書の作成に精通しています。
提供されたプロジェクト情報とアウトライン構造に基づいて、要求定義書の各セクションの詳細なコンテンツをマークダウン形式で作成してください。

考慮すべき点:
- 各セクションはプロジェクト情報に基づいた具体的な内容にする
- 不足している情報は合理的に推測して補完する
- 読みやすく、構造化されたマークダウン形式で出力する
- 図表の説明が必要な場合は、適切にプレースホルダーを入れる
- 専門用語は必要に応じて簡潔に説明を付ける
- 文書全体の一貫性と流れを保つ"""

        detail_user_msg = """以下のセクションのマークダウンコンテンツを作成してください:
セクション: {section_title}
見出し: {heading}

プロジェクト情報:
{project_info}

アウトライン構造:
{outline_structure}

思考プロセス（Chain of Thought）:
どのような思考プロセスでこの内容に至ったのか、具体的な理由や判断基準も合わせて説明してください。

重要: 応答は配列形式ではなく、単一のJSONオブジェクトとして返してください。

出力形式の指示に従い、JSONオブジェクトで結果を返してください:
{format_instructions}
"""
        parser = PydanticOutputParser(pydantic_object=DetailedSectionContent)
        prompt = ChatPromptTemplate.from_messages([('system', detail_system_msg), ('human', detail_user_msg)]).partial(
            project_info=requirement.model_dump_json(indent=2, exclude_none=True),
            outline_structure=dynamic_outline.model_dump_json(indent=2, exclude_none=True),
            format_instructions=parser.get_format_instructions(),
        )
        chain = prompt | llm | parser
        result = chain.ainvoke(
            {
                'section_title': section_title,
                'heading': heading,
            }
        )
        return result

    def _get_last_user_message(self, state: RequirementState) -> str:
        """最後のユーザーのメッセージを取得"""
        if state.get('messages', []) and isinstance(state['messages'][-1], HumanMessage):
            return state['messages'][-1].content
        else:
            return ''

    def _handle_special_commands(self, state: RequirementState, user_message: str) -> RequirementState:
        """ユーザーの特殊なコマンドを処理"""
        if user_message.lower() in ['ヘルプ', 'help', '用語', 'わからない言葉がある']:
            return {'user_wants_help': True}

        if any(
            keyword in user_message.lower()
            for keyword in [
                'ドキュメント作成',
                'document',
                '次へ進む',
                '完了',
                '終了',
                '次へ',
                'ドキュメント',
            ]
        ):
            ai_response = 'ありがとうございます。収集した情報を元に要求定義書を作成します。'
            updated_messages = state.get('messages', []) + [AIMessage(content=ai_response)]
            return {
                'messages': updated_messages,
                'current_phase': RequirementsPhase.OUTLINE_GENERATION,
                'requirement': state.get('requirement') or ProjectBusinessRequirement(),
                'interview_complete': True,
            }

        return None

    def _update_requirements(self, state: RequirementState, user_message: str) -> ProjectBusinessRequirement:
        """ユーザー入力に基づいて要件情報を更新"""
        current_requirement = state.get('requirement') or ProjectBusinessRequirement()
        if user_message and not state.get('user_wants_help', False):  # ヘルプコマンドの場合は更新しない
            current_requirement = self._parse_user_response(user_message, current_requirement)
            print(f'現在の収集済み要件:\n{current_requirement.model_dump_json(indent=2, exclude_none=True)}')

        return current_requirement

    def _parse_user_response(self, user_message: str, current_requirement: ProjectBusinessRequirement) -> ProjectBusinessRequirement:
        """ユーザーの回答を解析し、要件情報を更新"""
        current_info_json = current_requirement.model_dump_json(indent=2, exclude_none=True)

        parse_system_msg = """あなたは要求定義の専門家です。ユーザーの回答から要件情報を正確に抽出し、必要に応じて推論してください。

具体的な抽出・推論ルール：
1. ユーザーが明確に述べた情報を優先して抽出する
2. ユーザーが「わからない」「未定」などと答えた場合は、他の情報から合理的に推論する
   - 例: 予算が未定なら、規模から予算を推定（小規模なら100-500万円、中規模なら500-2000万円など）
   - 例: スケジュールが未定なら、類似プロジェクトの一般的な期間を提案
3. プロジェクト名は、明示的に言及された場合か、プロジェクトの内容から適切な名前を推測
4. ステークホルダーは役割や期待に関する情報も可能な限り抽出
5. 非機能要件は「速さ」「セキュリティ」「使いやすさ」などの言及から適切にカテゴリ分け
6. リスクは言及された課題から適切に抽出し、確率と影響度を推定
7. 法規制やコンプライアンスは業界や内容から関連する可能性の高いものを推測

推論を行う場合でも、あくまで現実的で妥当な範囲にとどめ、過度に具体的な仮定は避けてください。"""

        parse_user_msg = """現在の収集済み情報:
{current_info}

ユーザーからの最新の回答:
{user_message}

上記の情報に基づいて、ProjectBusinessRequirementスキーマに従って情報を更新・追記してください。
「わからない」「未定」などの回答には適切な推論を行い、その場合は推論であることが分かるように値を設定してください。
出力はスキーマに沿ったJSON形式でなければなりません。"""

        parser_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    'system',
                    parse_system_msg,
                ),
                (
                    'human',
                    parse_user_msg,
                ),
            ]
        ).partial(current_info=current_info_json)
        parser_chain = parser_prompt | llm.with_structured_output(ProjectBusinessRequirement)
        project_business_requirement: ProjectBusinessRequirement = parser_chain.invoke({'user_message': user_message})
        return project_business_requirement

    def _get_missing_mandatory_fields(self, requirement: ProjectBusinessRequirement | None) -> list[str]:
        """必須項目の中で不足しているフィールドを取得"""
        if requirement is None:
            return MANDATORY

        missing_fields = []
        data = requirement.model_dump()

        for field in MANDATORY:
            if field not in data or data[field] in (None, '', []):
                missing_fields.append(field)

        return missing_fields

    def _get_missing_optional_fields(self, requirement: ProjectBusinessRequirement | None) -> list[str]:
        """任意項目の中で不足しているフィールドを取得"""
        if requirement is None:
            return OPTIONAL

        missing_fields = []
        data = requirement.model_dump()

        for field in OPTIONAL:
            if field not in data or data[field] in (None, '', []):
                missing_fields.append(field)

        return missing_fields

    def _build_questions(self, missing_fields: list[str], batch_size: int = 3) -> str:
        """不足フィールドに関する質問文を構築"""
        questions = [QUESTION_TEMPLATES[field] for field in missing_fields[:batch_size]]
        return '\n'.join([f'- {question}' for question in questions])

    def _handle_updated_requirement_state(
        self, current_requirement: ProjectBusinessRequirement, state: RequirementState
    ) -> RequirementState:
        """要件情報が更新された場合の処理"""
        missing_mandatory_fields = self._get_missing_mandatory_fields(current_requirement)
        missing_optional_fields = self._get_missing_optional_fields(current_requirement)
        is_user_responded = state.get('messages', []) and isinstance(state['messages'][-1], HumanMessage)

        if missing_mandatory_fields:  # 必須項目が揃っていない場合
            ai_response = self._generate_ai_response_incomplete_mandatory_case(is_user_responded, missing_mandatory_fields)
            updated_message = state.get('messages', []) + [AIMessage(content=ai_response)]
            return {
                'messages': updated_message,
                'requirement': current_requirement,
                'current_phase': RequirementsPhase.INTERVIEW,
                'interview_complete': False,
            }

        # 必須項目が揃っている場合
        is_asked_for_optional = state.get('asked_for_optional', False)
        ai_response = self._generate_ai_response_complete_madatory_case(is_asked_for_optional, missing_optional_fields)
        updated_message = state.get('messages', []) + [AIMessage(content=ai_response)]
        return {
            'messages': updated_message,
            'requirement': current_requirement,
            'asked_for_optional': True,
        }

    def _generate_ai_response_complete_madatory_case(self, is_asked_for_optional: bool, missing_optional_fields: list[str]) -> str:
        """必須項目が揃った場合の応答を生成"""
        if missing_optional_fields and is_asked_for_optional:  # 任意項目が不足している場合
            optional_questions = self._build_questions(missing_optional_fields[:2])
            return f"""
必要な主要情報が揃いました！ありがとうございます。

さらに詳細な要求定義書を作成するため、よろしければ以下の項目についても教えていただけますか：
{optional_questions}

これらは任意の項目ですので、わからない場合や決まっていない場合は「次へ」とお答えいただければ先に進みます。
すべての情報が揃ったら、または先に進みたい場合は「ドキュメント作成」とおっしゃってください。
"""

        # すでにオプション項目も尋ねた場合、または全て揃った場合
        return """
ありがとうございます。必要な情報が揃いましたので、ドキュメント作成に進みたい場合は「ドキュメント作成」とおっしゃってください。
他に追加したい情報があれば、お知らせください。
"""

    def _generate_ai_response_incomplete_mandatory_case(self, is_user_responded: bool, missing_mandatory_fields: list[str]) -> str:
        """必須項目が不足している場合の応答を生成"""
        questions_to_ask = self._build_questions(missing_mandatory_fields)
        if not is_user_responded:  # ユーザーがまだ何も答えていない場合（初めての質問）
            return f"""プロジェクトについて詳しく教えていただけますか？

例えば、以下のような点です：
{questions_to_ask}

わからない項目があれば「わからない」とお伝えください。
"""
        # ユーザーが何か答えた場合
        return f"""ありがとうございます。

次に、以下の点について教えていただけますか？
{questions_to_ask}

わからない項目があれば「わからない」とお伝えください。推測してみます。
また、専門用語の説明が必要な場合は「ヘルプ」とおっしゃってください。
"""

    def _saved_document(self, requirement_document: RequirementDocument, file_path: str) -> None:
        """生成した要求定義書をファイルに保存"""
        if not requirement_document.markdown_text:
            raise ValueError('RequirementDocument is empty.')

        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(requirement_document.markdown_text)

        print(f'ファイルを保存しました: {file_path}')
