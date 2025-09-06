"""
CLI for AI Text Humanizer
"""
import argparse
from .core import humanize_text

def main():
    parser = argparse.ArgumentParser(description="AI Text Humanizer CLI (English & Persian)")
    parser.add_argument("-t", "--text", type=str, help="Input text (or use -f)")
    parser.add_argument("-f", "--file", type=str, help="Input file path")
    parser.add_argument("-l", "--language", type=str, default="en", choices=["en", "fa"], help="Language: en/fa")
    parser.add_argument("-e", "--engine", type=str, default="default", help="Engine: default/hazm/stanza/combo")
    parser.add_argument("--no-stopwords", action="store_true", help="(fa) Do not remove stopwords")
    parser.add_argument("--no-lemmatize", action="store_true", help="(fa) Do not lemmatize")
    parser.add_argument("--no-stem", action="store_true", help="(fa) Do not stem")
    args = parser.parse_args()

    if args.text:
        text = args.text
    elif args.file:
        with open(args.file, encoding="utf-8") as f:
            text = f.read()
    else:
        print("Please provide input text with -t or a file with -f.")
        return

    kwargs = {}
    if args.language == "fa" and args.engine == "hazm":
        kwargs["remove_stopwords"] = not args.no_stopwords
        kwargs["use_lemmatize"] = not args.no_lemmatize
        kwargs["use_stem"] = not args.no_stem

    result = humanize_text(text, language=args.language, engine=args.engine, **kwargs)
    print(result)

if __name__ == "__main__":
    main()
