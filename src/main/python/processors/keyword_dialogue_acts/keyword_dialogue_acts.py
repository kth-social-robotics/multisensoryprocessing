#!/usr/bin/env python3

import csv
import re
import sys
from collections import defaultdict, Counter

import nltk
import yaml

sys.path.append('../..')
from shared import MessageQueue

# Settings
SETTINGS_FILE = '../../settings.yaml'

COL_SEP = "\t"
DA_LABEL_COL_NAME = "DA"
PHRASE_COL_NAME = "PHRASE"
USERNAME_PLACEHOLDER_TOKEN = "<user>"
WHITESPACE_PATTERN = re.compile("\\s+")

with open(SETTINGS_FILE, 'r') as settings_inf:
	settings = yaml.safe_load(settings_inf)
	env_exchange_name = settings["messaging"]["environment"]

class DialogueActTargets(object):
	def __init__(self, target_da_label_counts):
		self.target_da_label_counts = target_da_label_counts
		self.total_label_count = sum_embedded_dict_values(target_da_label_counts)
		self.target_da_label_likelihoods = create_da_label_likelihood_dict(target_da_label_counts,
																		   float(self.total_label_count))

	def __repr__(self):
		return self.__class__.__name__ + str(self.__dict__)

class PhraseDALabeller(object):

    def __init__(self, phrase_da_labels, usernames, ngram_factory=nltk.bigrams):
        self.phrase_da_labels = phrase_da_labels
        self.ngram_da_labels = self._create_ngram_da_label_dict(phrase_da_labels, ngram_factory)
        self.usernames = usernames
        self.ngram_factory = ngram_factory

    def find_phrase_da_labels(self, phrase_tokens):
        result = {}
		# TODO: Reverse key-value pairs so that the result looks like "{da_label : {target : count}}"
        user_placeholder_phrases = dict((username, tuple(USERNAME_PLACEHOLDER_TOKEN if token == username else token for token in phrase_tokens)) for username in self.usernames)
        for username in self.usernames:
            phrase_tokens_with_placeholder = user_placeholder_phrases[username]
            da_labels = self._find_exact_phrase_da_labels(phrase_tokens_with_placeholder)
            if len(da_labels) > 0:
                result[username] = da_labels

        if len(result) == 0:
            for username in self.usernames:
                phrase_tokens_with_placeholder = user_placeholder_phrases[username]
                da_labels = self._find_ngram_da_labels(phrase_tokens_with_placeholder)
                if len(da_labels) > 0:
                    result[username] = da_labels

        return result

    def _create_ngram_da_label_dict(self, phrase_da_labels, ngram_factory):
        result = {}
        for phrase, da_label in phrase_da_labels.items():
            phrase_bigrams = ngram_factory(phrase)
            for bigram in phrase_bigrams:
                result[bigram] = da_label
        return result

    def _find_exact_phrase_da_labels(self, phrase_tokens_with_placeholder):
        result = defaultdict(Counter)
        # TODO: Replace this with a suffix tree to improve performance
        for subseq_length in range(len(phrase_tokens_with_placeholder), 0, -1):
            subseqs = nltk.ngrams(phrase_tokens_with_placeholder, subseq_length)
            for subseq in subseqs:
                subseq_labels = self.phrase_da_labels.get(subseq)
                if subseq_labels is not None:
                    result[subseq].update(subseq_labels)
        return result

    def _find_ngram_da_labels(self, phrase_tokens):
        result = defaultdict(Counter)
        phrase_ngrams = self.ngram_factory(phrase_tokens)
        for ngram in phrase_ngrams:
            ngram_labels = self.ngram_da_labels.get(ngram)
            if ngram_labels is not None:
                result[ngram].update(ngram_labels)
        return result

def create_phrase_da_label_dict(rows):
	result = defaultdict(Counter)
	col_name_idxs = dict((col_name, idx) for (idx, col_name) in enumerate(next(rows)))
	for row in rows:
		phrase = row[col_name_idxs[PHRASE_COL_NAME]]
		phrase_tokens = tuple(WHITESPACE_PATTERN.split(phrase))
		da_label = row[col_name_idxs[DA_LABEL_COL_NAME]]
		result[phrase_tokens][da_label] += 1

	return result

def create_da_label_likelihood_dict(target_da_label_counts, total_label_count):
	user_label_total_counts = defaultdict(Counter)
	for username, label_counts in target_da_label_counts.items():
		label_total_counts = user_label_total_counts[username]
		for phrase, da_counts in label_counts.items():
			label_total_counts.update(da_counts)

	result = {}
	for username, da_label_counts in user_label_total_counts.items():
		da_label_likelihoods = dict(
			(da_label, count / total_label_count) for da_label, count in da_label_counts.items())
		result[username] = da_label_likelihoods
	return result

def create_phrase_da_labeller(dialogue_category_inpath, player_names):
	with open(dialogue_category_inpath, 'r') as lines:
		rows = csv.reader(lines, delimiter=COL_SEP, skipinitialspace=True)
		phrase_da_labels = create_phrase_da_label_dict(rows)
	print("Read phrase label dict of size %d." % len(phrase_da_labels), file=sys.stderr)

	return PhraseDALabeller(phrase_da_labels, player_names)

def sum_embedded_dict_values(d):
	result = 0
	for embedded_dict in d.values():
		for embedded_counter in embedded_dict.values():
			result += sum(embedded_counter.values())
	return result

# Process input data
def callback(_mq, get_shifted_time, routing_key, body):
    input_tokens = WHITESPACE_PATTERN.split(body["text"])
    _mq.publish(exchange=env_exchange_name,
                routing_key=settings["messaging"]["dialogue_acts"],
                body={'participant':'test'})
    da_labels = phrase_da_labeller.find_phrase_da_labels(input_tokens)
#	print(da_labels, file=sys.stderr)
    da_targets = DialogueActTargets(da_labels)
	#	print(da_targets, file=sys.stderr)

	# Reverse key-value pairs
    da_label_targets = defaultdict(dict)
    for target, da_label_likelihoods in da_targets.target_da_label_likelihoods.items():
        for da_label, likelihood in da_label_likelihoods.items():
            target_likelihoods = da_label_targets[da_label]
            target_likelihoods[target] = likelihood

    participant = routing_key.rsplit('.', 1)[1]
    data = {
        "participant": participant,
        "dialogue-acts" : da_label_targets
	}
    _mq.publish(exchange=env_exchange_name,
                routing_key=settings["messaging"]["dialogue_acts"] + ".{}".format(participant),
                body=data)

if __name__ == "__main__":
    player_names = set(player["name"] for player in settings["players"])
    print("Player usernames to use during keyword detection: %s", player_names, file=sys.stderr)
    phrase_da_labeller = create_phrase_da_labeller("phrase_da_labels.tsv", player_names)

	# Testing -----------------------------------------------
#	input = "I accuse orange because she has been talking a lot but white is a villager"
#	print("Test input: %s" % input)
#	input_tokens = WHITESPACE_PATTERN.split(input)
#	da_labels = phrase_da_labeller.find_phrase_da_labels(input_tokens)
#	print(da_labels)
#	da_targets = DialogueActTargets(da_labels)
#	print(da_targets)
	# -------------------------------------------------------

    mq = MessageQueue('keyword-dialogue-act-processor')
    mq.bind_queue(exchange='pre-processor', routing_key="{}.*".format(settings['messaging']['asr_watson']), callback=callback)
    print('[*] Waiting for messages. To exit press CTRL+C')
    mq.listen()
