import pickle
import os
from data import TRAINING_DATA

_trained_model = None
MODEL_FILE = "model.pkl"


def get_model():
    global _trained_model
    if _trained_model is None:
        if os.path.exists(MODEL_FILE):
            with open(MODEL_FILE, "rb") as f:
                _trained_model = pickle.load(f)
        else:
            _trained_model = train()
            with open(MODEL_FILE, "wb") as f:
                pickle.dump(_trained_model, f)
    return _trained_model


def get_words(sentence):
    words = []
    word = ""
    for ch in sentence.lower():
        if ch.isalpha() or ch == "'":
            word += ch
        else:
            if word:
                words.append(word)
            word = ""
    if word:
        words.append(word)
    return words


def train():
    task_word_counts = {}
    not_task_word_counts = {}
    task_total = 0
    not_task_total = 0
    task_sentences = 0
    not_task_sentences = 0

    for sentence, label in TRAINING_DATA:
        words = get_words(sentence)
        if label == 1:
            task_sentences += 1
            for word in words:
                task_total += 1
                task_word_counts[word] = task_word_counts.get(word, 0) + 1
        else:
            not_task_sentences += 1
            for word in words:
                not_task_total += 1
                not_task_word_counts[word] = not_task_word_counts.get(word, 0) + 1

    total_sentences = task_sentences + not_task_sentences
    prob_task = task_sentences / total_sentences
    prob_not_task = not_task_sentences / total_sentences

    vocab_size = len(set(list(task_word_counts.keys()) + list(not_task_word_counts.keys())))

    return {
        "task_word_counts":     task_word_counts,
        "not_task_word_counts": not_task_word_counts,
        "task_total":           task_total,
        "not_task_total":       not_task_total,
        "prob_task":            prob_task,
        "prob_not_task":        prob_not_task,
        "vocab_size":           vocab_size,
    }


def predict(sentence, model):
    words = get_words(sentence)

    score_task = model["prob_task"]
    score_not_task = model["prob_not_task"]

    for word in words:
        task_count = model["task_word_counts"].get(word, 0)
        not_task_count = model["not_task_word_counts"].get(word, 0)

        prob_word_given_task = (task_count + 1) / (model["task_total"] + model["vocab_size"])
        prob_word_given_not_task = (not_task_count + 1) / (model["not_task_total"] + model["vocab_size"])

        score_task *= prob_word_given_task
        score_not_task *= prob_word_given_not_task

    return 1 if score_task > score_not_task else 0
