import numpy as np
from utils import *


def error_matrix(prob_list, token_list, label_list, vocab, **kwargs):
    """
    :param prob_list: list
    :param token_list: list
    :param label_list: list
    :param vocab: dict, map str to int
    :return:
    """
    assert len(prob_list) == len(token_list)
    assert len(prob_list) == len(label_list)

    token_idx_list = lookup_vocab4line(token_list, vocab)
    vocab_size = len(vocab)

    prob_array = np.array(prob_list)
    label_array = np.array(label_list)
    token_idx_array = np.array(token_idx_list)
    value_array = label_array - prob_array

    bins = kwargs.get("bins") or 20
    bin_width = 1.0 / bins
    list_len = len(prob_list)
    err_matrix = np.zeros((bins, vocab_size))
    count_matrix = np.zeros((bins, vocab_size))
    prob_matrix = np.zeros((bins, vocab_size))
    for i in range(bins):
        lower_bound = i * bin_width
        upper_bound = (i + 1) * bin_width
        if i < bins - 1:
            cond = (prob_array >= lower_bound) & (prob_array < upper_bound)
        else:
            cond = (prob_array >= lower_bound) & (prob_array <= upper_bound)
        for j in range(list_len):
            if cond[j]:
                err_matrix[i][token_idx_array[j]] += value_array[j]
                prob_matrix[i][token_idx_array[j]] += prob_array[j]
                count_matrix[i][token_idx_array[j]] += 1

    assert list_len == np.sum(count_matrix)

    hit_matrix = err_matrix + prob_matrix

    return err_matrix, hit_matrix, prob_matrix, count_matrix


def calculate_ece(emtrx, cmtrx):
    return np.sum(np.abs(np.sum(emtrx, axis=1))) / np.sum(cmtrx)


def calculate_token_ece(emtrx, cmtrx):
    return np.sum(np.abs(emtrx)) / np.sum(cmtrx)


def extract_bin_info(hmtrx, cmtrx):
	"""
	:param hmtrx: np.array(bins, vocab_size)
    :param cmtrx: np.array(bins, vocab_size)
    :return: acc_list, gap_list, count_list
	"""
	count_array = np.sum(cmtrx, axis=1)
	count_list = count_array.tolist()
	acc_list = (np.sum(hmtrx, axis=1) / count_array).tolist()
	bins = len(count_list)
	bin_width = 1.0 / bins
	prob_list = [bin_width / 2 + bin_width * i for i in range(bins)]
	gap_list = [p - a for p, a in zip(prob_list, acc_list)]

	return acc_list, gap_list, count_list