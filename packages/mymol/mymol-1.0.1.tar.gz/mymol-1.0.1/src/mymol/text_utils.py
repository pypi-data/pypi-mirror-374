from nltk.corpus import wordnet
from wordcloud import WordCloud
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from spellchecker import SpellChecker

def count_words(text: str) -> int:
    """
    Count the number of words in a given text.

    Args:
        text (str): The input text to count words from.

    Returns:
        int: The number of words in the input text.

    Examples:
        >>> count_words("Hello world")
        2
        >>> count_words("This is a test sentence.")
        5
    """
    return len(text.split())

def find_word_frequency(text: str) -> dict:
    """
    Find the frequency of each word in the given text.

    Args:
        text (str): The input text to find word frequency from.

    Returns:
        dict: A dictionary containing the frequency of each word in the input text.

    Examples:
        >>> find_word_frequency("Hello world")
        {'Hello': 1, 'world': 1}
        >>> find_word_frequency("This is a test sentence.")
        {'This': 1, 'is': 1, 'a': 1, 'test': 1, 'sentence.': 1}
    """
    words = text.split()
    freq = {}
    for word in words:
        freq[word] = freq.get(word, 0) + 1
    return freq

def remove_punctuation(text: str) -> str:
    """
    Remove punctuation from the given text.

    Args:
        text (str): The input text to remove punctuation from.

    Returns:
        str: The input text with punctuation removed.

    Examples:
        >>> remove_punctuation("Hello, world!")
        'Hello world'
        >>> remove_punctuation("This is a test sentence.")
        'This is a test sentence'
    """
    return ''.join([c for c in text if c.isalnum() or c.isspace()])

def find_longest_word(text: str) -> str:
    """
    Find the longest word in the given text.

    Args:
        text (str): The input text to find the longest word from.

    Returns:
        str: The longest word in the input text.

    Examples:
        >>> find_longest_word("Hello world")
        'Hello'
        >>> find_longest_word("This is a test sentence.")
        'sentence'
    """
    words = text.split()
    return max(words, key=len)

def extract_numbers(text: str) -> list:
    """
    Extract numbers from the given text.

    Args:
        text (str): The input text to extract numbers from.

    Returns:
        list: A list of numbers extracted from the input text.

    Examples:
        >>> extract_numbers("Hello 123 world")
        [123]
        >>> extract_numbers("This is a test sentence.")
        []
    """
    return [int(word) for word in text.split() if word.isdigit()]

from spellchecker import SpellChecker

def spell_checker(text: str) -> str:
    """
    Perform spell checking on the given text.

    Args:
        text (str): The input text to perform spell checking on.

    Returns:
        str: The input text with spelling mistakes corrected.

    Examples:
        >>> spell_checker("Helo world")
        'Hello world'
        >>> spell_checker("This is a test sentance.")
        'This is a test sentence.'
    """
    spell = SpellChecker()
    corrected_text = [spell.correction(word) if word else word for word in text.split()]
    return ' '.join(corrected_text)


def generate_word_cloud(text: str) -> None:
    """
    Generate a word cloud from the given text.

    Args:
        text (str): The input text to generate a word cloud from.

    Returns:
        None

    Examples:
        >>> generate_word_cloud("Hello world")
        None
        >>> generate_word_cloud("This is a test sentence.")
        None
    """


    wordcloud = WordCloud(width=800, height=400).generate(text)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.show()

def text_summarizer(text: str, num_sentences: int) -> str:
    """
    Summarize the given text to a specified number of sentences.

    Args:
        text (str): The input text to summarize.
        num_sentences (int): The number of sentences to summarize the text to.

    Returns:
        str: The summarized text.

    Examples:
        >>> text_summarizer("Hello world. This is a test sentence.", 1)
        'Hello world.'
        >>> text_summarizer("This is a test sentence.", 3)
        'This is a test sentence.'
    """
    sentences = text.split('.')
    if len(sentences) <= num_sentences:
        return text

    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform(sentences)
    kmeans = KMeans(n_clusters=num_sentences)
    kmeans.fit(X)

    summarized_sentences = []
    for i in range(num_sentences):
        cluster_center = kmeans.cluster_centers_[i]
        closest_sentence_idx = X.dot(cluster_center.T).argmax()
        summarized_sentences.append(sentences[closest_sentence_idx])

    return '. '.join(summarized_sentences) + '.'

def find_synonyms(word: str) -> list:
    """
    Find synonyms of the given word.

    Args:
        word (str): The input word to find synonyms of.

    Returns:
        list: A list of synonyms of the input word.

    Examples:
        >>> find_synonyms("happy")
        ['glad', 'joyful', 'content', 'pleased', 'satisfied']
        >>> find_synonyms("sad")
        ['unhappy', 'sorrowful', 'dejected', 'miserable', 'downcast']
    """
    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name())
    return list(synonyms)

def text_sentiment_analysis(text: str) -> str:
    """
    Perform sentiment analysis on the given text.

    Args:
        text (str): The input text to perform sentiment analysis on.

    Returns:
        str: The sentiment of the input text.

    Examples:
        >>> text_sentiment_analysis("I am happy")
        'positive'
        >>> text_sentiment_analysis("I am sad")
        'negative'
    """
    positive_words = [
        'happy', 'joyful', 'excited', 'positive', 'good', 'pleased', 'content', 'satisfied', 'cheerful', 'delighted',
        'ecstatic', 'elated', 'enthusiastic', 'euphoric', 'exhilarated', 'glad', 'jubilant', 'lively', 'merry', 'optimistic',
        'overjoyed', 'radiant', 'thrilled', 'upbeat', 'vibrant', 'blissful', 'buoyant', 'chipper', 'gleeful', 'grateful',
        'hopeful', 'inspired', 'jovial', 'lighthearted', 'loving', 'motivated', 'peaceful', 'perky', 'refreshed', 'rejuvenated',
        'spirited', 'sunny', 'uplifted', 'vivacious', 'zestful'
    ]
    negative_words = [
        'sad', 'unhappy', 'depressed', 'negative', 'bad', 'angry', 'annoyed', 'anxious', 'apprehensive', 'bitter',
        'blue', 'cheerless', 'dejected', 'despondent', 'disappointed', 'discontented', 'dismal', 'distressed', 'downcast',
        'downhearted', 'forlorn', 'frustrated', 'gloomy', 'glum', 'grief-stricken', 'heartbroken', 'hopeless', 'irate',
        'irritable', 'melancholy', 'miserable', 'morose', 'nervous', 'pessimistic', 'regretful', 'resentful', 'sorrowful',
        'troubled', 'upset', 'weary', 'woeful', 'worried', 'wretched'
    ]

    num_positive_words = sum(1 for word in text.split() if word in positive_words)
    num_negative_words = sum(1 for word in text.split() if word in negative_words)

    if num_positive_words > num_negative_words:
        return 'positive'
    elif num_negative_words > num_positive_words:
        return 'negative'
    else:
        return 'neutral'