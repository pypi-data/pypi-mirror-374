from vital_llm_reasoner.tool.web_extract_tool import WebExtractTool


def main():
    urls = [
        # "https://www.yahoo.com"
        "https://www.cartercenter.org/about/experts/jimmy_carter.html",
        # "http://badurl.nothing"
    ]

    results = WebExtractTool.extract(urls)

    for result in results:
        print(f"URL: {result.url}")
        print(f"Status: {result.status.value}")
        # print(f"Extracted Markdown:\n{result.text[:500]}...\n")
        print(f"Extracted Markdown:\n{result.text}")

if __name__ == "__main__":
    main()
