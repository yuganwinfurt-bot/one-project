import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from app.rag import graph, pipeline


class RetrievalTests(unittest.TestCase):
    def test_irrelevant_candidates_are_removed_before_answering(self):
        class Store:
            def get(self, **_kwargs):
                return {"ids": ["existing"]}

            def similarity_search_with_relevance_scores(self, _question, k):
                self.requested_k = k
                return [
                    (SimpleNamespace(page_content="无关内容", metadata={"filename": "bad.txt"}), 0.1),
                    (SimpleNamespace(page_content="正确内容", metadata={"filename": "good.txt"}), 0.8),
                ]

        with patch.object(pipeline, "get_vector_store", return_value=Store()):
            hits = pipeline.retrieve_contexts("设备如何接线", ["kb"], {"kb": "测试库"})
        self.assertEqual([item["filename"] for item in hits], ["good.txt"])

    def test_mixed_text_and_scanned_pdf_pages_are_merged(self):
        text_pages = [
            SimpleNamespace(page_content="文字" * 200, metadata={"page": 0}),
            SimpleNamespace(page_content="", metadata={"page": 1}),
        ]
        image_pages = [
            SimpleNamespace(page_content="旧识别文本", metadata={"page": 0}),
            SimpleNamespace(page_content="扫描页上的接线表", metadata={"page": 1}),
        ]
        image_parse_calls = []

        class Loader:
            def __init__(self, _path, extract_images=False, **_kwargs):
                self.extract_images = extract_images
                if extract_images:
                    image_parse_calls.append(True)

            def load(self):
                return image_pages if self.extract_images else text_pages

        with patch.object(pipeline, "PyPDFLoader", Loader), patch.object(
            pipeline, "RapidOCRBlobParser", return_value=object()
        ):
            result = pipeline.load_pdf(Path("mixed.pdf"))
        self.assertEqual(result[0].page_content, "文字" * 200)
        self.assertEqual(result[1].page_content, "扫描页上的接线表")
        self.assertEqual(len(image_parse_calls), 1)


class FollowupTests(unittest.IsolatedAsyncioTestCase):
    async def test_followup_query_includes_previous_subject(self):
        requests = []

        class Model:
            async def ainvoke(self, messages):
                requests.append(messages)
                return SimpleNamespace(content="KPZ32 控制板串口如何接线？")

        with patch.object(graph, "ChatOllama", return_value=Model()):
            query = await graph.rewrite_query(
                "那它怎么接线？",
                [{"role": "user", "content": "KPZ32 控制板的串口在哪里？"}],
            )
        self.assertEqual(query, "KPZ32 控制板串口如何接线？")
        self.assertIn("KPZ32", requests[0][1].content)

    async def test_first_question_does_not_call_rewrite_model(self):
        with patch.object(graph, "ChatOllama") as model:
            query = await graph.rewrite_query("STM32F103 的串口在哪里？", [])
        self.assertEqual(query, "STM32F103 的串口在哪里？")
        model.assert_not_called()


if __name__ == "__main__":
    unittest.main()
