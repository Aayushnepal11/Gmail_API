from gmail_api import GmailAPI

if __name__ == '__main__':
    g1 = GmailAPI()
    g1.set_labels("inbox", max_results=10)
