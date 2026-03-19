"""
Monkey-patch lib_resume_builder_AIHawk to use Playwright instead of Selenium.

Import this module early (before any lib_resume_builder_AIHawk usage) to
replace its Selenium-based utilities with Playwright equivalents.
"""
import base64

from src.utils.chrome_utils import _get_browser, HTML_to_PDF


def _create_driver_playwright():
    """Replacement for lib_resume_builder_AIHawk.utils.create_driver_selenium."""
    browser = _get_browser()
    page = browser.new_page(viewport={"width": 1200, "height": 800})
    return page


def _html_to_pdf_from_file(file_path):
    """Replacement for lib_resume_builder_AIHawk.utils.HTML_to_PDF (file-based)."""
    import os
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The specified file does not exist: {file_path}")

    file_url = f"file:///{os.path.abspath(file_path).replace(os.sep, '/')}"
    page = _create_driver_playwright()
    try:
        page.goto(file_url, wait_until="networkidle")
        pdf_bytes = page.pdf(
            print_background=True,
            landscape=False,
            width="8.27in",
            height="11.69in",
            margin={
                "top": "0.8in",
                "bottom": "0.8in",
                "left": "0.5in",
                "right": "0.5in",
            },
            prefer_css_page_size=True,
        )
        return base64.b64encode(pdf_bytes).decode("utf-8")
    except Exception as e:
        raise RuntimeError(f"Playwright PDF generation error: {e}")
    finally:
        page.close()


def apply_patch():
    """Apply the Playwright monkey-patch to lib_resume_builder_AIHawk."""
    try:
        import lib_resume_builder_AIHawk.utils as lib_utils
        lib_utils.create_driver_selenium = _create_driver_playwright
        lib_utils.HTML_to_PDF = _html_to_pdf_from_file
    except ImportError:
        pass

    # Also patch the job description module's inline import
    try:
        import lib_resume_builder_AIHawk.gpt_resume_job_description as jd_mod

        _original_set_jd = jd_mod.LLMResumeJobDescription.set_job_description_from_url

        def _patched_set_jd(self, url_job_description):
            import os
            import tempfile
            from langchain_community.document_loaders import TextLoader
            from langchain_core.output_parsers import StrOutputParser
            from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
            from langchain_core.runnables import RunnablePassthrough
            from langchain_community.embeddings import OpenAIEmbeddings
            from langchain_community.vectorstores import FAISS
            from langchain_text_splitters import TokenTextSplitter

            page = _create_driver_playwright()
            page.goto(url_job_description, wait_until="networkidle")
            response = page.locator("body").inner_html()
            page.close()

            with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8") as temp_file:
                temp_file.write(response)
                temp_file_path = temp_file.name
            try:
                loader = TextLoader(temp_file_path, encoding="utf-8", autodetect_encoding=True)
                document = loader.load()
            finally:
                os.remove(temp_file_path)

            text_splitter = TokenTextSplitter(chunk_size=500, chunk_overlap=50)
            all_splits = text_splitter.split_documents(document)
            vectorstore = FAISS.from_documents(documents=all_splits, embedding=self.llm_embeddings)
            prompt = PromptTemplate(
                template="""
                You are an expert job description analyst. Your role is to meticulously analyze and interpret job descriptions.
                After analyzing the job description, answer the following question in a clear, and informative manner.

                Question: {question}
                Job Description: {context}
                Answer:
                """,
                input_variables=["question", "context"]
            )

            def format_docs(docs):
                return "\n\n".join(doc.page_content for doc in docs)

            context_formatter = vectorstore.as_retriever() | format_docs
            question_passthrough = RunnablePassthrough()
            chain_job_description = prompt | self.llm_cheap | StrOutputParser()
            summarize_prompt_template = self._preprocess_template_string(self.strings.summarize_prompt_template)
            prompt_summarize = ChatPromptTemplate.from_template(summarize_prompt_template)
            chain_summarize = prompt_summarize | self.llm_cheap | StrOutputParser()
            qa_chain = (
                {
                    "context": context_formatter,
                    "question": question_passthrough,
                }
                | chain_job_description
                | (lambda output: {"text": output})
                | chain_summarize
            )
            result = qa_chain.invoke("Provide, full job description")
            self.job_description = result

        jd_mod.LLMResumeJobDescription.set_job_description_from_url = _patched_set_jd
    except ImportError:
        pass
