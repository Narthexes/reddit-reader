import praw
import time
import spacy

nlp = spacy.load('en')

class Node:
    def __init__(self, headline, focus, p_score, n_score):
        self.headline = headline
        self.focus = focus
        self.p_score = p_score
        self.n_score = n_score
        self.score = self.p_score + self.n_score
        self.next = None

class LinkedList:
    def __init__(self, node):
        self.head = node
        if node is None:
            self.length = 0
        else:
            self.length = 1

    def search(self, node):
        cur = self.head
        while cur is not None:
            if cur.focus.lower() == node.focus.lower():
                return cur
            cur = cur.next
        return None

    def insert(self, node): #self sorting
        temp = self.search(node)
        if self.head is None:
            self.head = node
        elif temp is not None:
            temp.p_score += node.p_score
            temp.n_score += node.n_score
            temp.score += node.score
            self.sort()
        elif node.score <= self.head.score:
            node.next = self.head
            self.head = node
        else:
            cur = self.head
            while cur.next is not None and node.score >= cur.next.score: #stops when cur is now a larger val than node
                cur = cur.next
            node.next = cur.next
            cur.next = node
        self.length += 1
        self.sort()

    def sort(self): #lazy way of keeping the score order intact
        for out_cur in range(self.length-1, 0, -1):
            swap = False
            first_bubble = self.head
            for in_cur in range(out_cur):
                if first_bubble.next is not None and first_bubble.score >  first_bubble.next.score:
                    temp = first_bubble.next
                    first_bubble.next = temp.next
                    temp.next = first_bubble
                    if first_bubble is self.head:
                        self.head = temp
                    swap = True
                    if swap is False:
                        return

    def print(self):
        print("========================\n")
        cur = self.head
        while cur is not None:
            print(str(cur.headline) + "\n\tSubject [" + str(cur.focus) + "] " + str(cur.score) + "\n\t" + "Pos score = " + str(cur.p_score) + " Neg score = " + str(cur.n_score))
            cur = cur.next
        print("\n========================")


def get_effect(word): #parses the  file and tries to return a value for a given word.
    negative = open("negative-words.txt")
    positive = open("positive-words.txt")
    for line in negative:
        if word in line:
                return -1
    for line in positive:
        if word in line:
                return 1
    return 0


bot = praw.Reddit(user_agent='Tester by /u/Nars_Bot',
                  client_id='######',
                  client_secret='######',
                  username='######',
                  password='######')

subreddit = bot.subreddit('news')
targetRedditor = bot.redditor('######')

posts = subreddit.stream.submissions()
list = LinkedList(None)

print("Polling start!")

for post in posts:
        print("We are starting a new thread!")
        title = str(post.title)
        text = str(post.selftext)
        doc = nlp(title)
        focus = ""
        subject = ""
        for terms in doc:
            if terms.dep_ == "nsubj":
                subject = terms
                break               #we gain our subject here in a simple sentence

        if subject is not None:
            focus = str(subject)
        else:
            print("The title could not be resolved.")
            print(doc)
            focus = "unresolved"
        positive_score = 0
        negative_score = 0

        for word in text.split():
            result = get_effect(word) #adjust the score based on submission's text. Doubt this would have any good or bad words.
            if result == 1:
                positive_score += 1
            elif result == -1:
                negative_score -= 1

        post.comments.replace_more(limit=0)
        for comment in post.comments.list():
            body = str(comment.body)
            for word in comment.body.split():
                result = get_effect(word)  # adjust the score based on submission's text. Doubt this would have any good or bad words.
                if result == 1:
                    positive_score += 1
                elif result == -1:
                    negative_score -= 1

        node = Node(title, focus, positive_score, negative_score) #make a new node
        list.insert(node)
        list.print()
        time.sleep(3)
