"""
Benchmarking on __contains__ method for various containers.

"""
import csv
import sys
import random
import itertools
from timeit import timeit
from functools import partial


RUN_NUMBER        = 1000
DATA_SIZE_MIN     = 1  # minimal number of element in the container
DATA_SIZE_MAX     = 10  # maximal number of element in the container
CONTAINERS        = (list, tuple, set, frozenset)
DATA_TYPES        = (int, str)  # functions data_gen_*
LETTERS           = tuple(chr(c) for c in range(32, 127))

DEFAULT_CSV_FILENAME = 'statistics_{}.csv'
CSV_FIELD_ELEM = 'existing'
CSV_FIELD_NONE = 'missing'
CSV_TIME_FIELDS = tuple(itertools.product(CONTAINERS, (CSV_FIELD_ELEM, CSV_FIELD_NONE)))
CSV_FIELDS = (
    'data size',
    *(container.__name__ + ' ' + elem + ' time'
      for container, elem in CSV_TIME_FIELDS)
)

BAR_WIDTH = 78  # width of the loading bar drawn


def save_scores_csv(data_size, scores, csv_writer):
    assert isinstance(scores, dict)
    assert all(container in CONTAINERS for container in scores)
    assert all(isinstance(subscore, dict) for subscore in scores.values())
    assert all(isinstance(score, float)
               for subscores in scores.values() for score in subscores.values())
    csv_writer.writerow(
        [data_size] + [scores[container][elem]
            for container, elem in CSV_TIME_FIELDS
        ]
    )


def raw_data_int(data_size):
    return random.sample(range(data_size*1000), data_size)


def raw_data_str(data_size, size=100):
    return tuple(''.join(random.choice(LETTERS) for _ in range(size))
                 for _ in range(data_size))

def raw_data_generators():
    """Return tuple of all functions raw_data_* for all DATA_TYPES"""
    return tuple(globals()['raw_data_' + cls.__name__] for cls in DATA_TYPES)


if __name__ == '__main__':
    benchmark = partial(timeit, number=RUN_NUMBER)
    gens_suffix = tuple(gen.__name__[gen.__name__.rfind('_')+1:]
                        for gen in raw_data_generators())

    csv_writers = {  # {type: csv writer}
        suffix: csv.writer(open(DEFAULT_CSV_FILENAME.format(suffix), 'w'))
        for suffix in gens_suffix
    }
    for writer in csv_writers.values():
        writer.writerow(CSV_FIELDS)  # header

    for data_size in range(DATA_SIZE_MIN, DATA_SIZE_MAX+1):
        percent = (data_size - DATA_SIZE_MIN) / (DATA_SIZE_MAX - DATA_SIZE_MIN)
        print('\r[' + ('>' * int(percent * BAR_WIDTH)).ljust(BAR_WIDTH) + ']', end='')
        sys.stdout.flush()
        for data_gen in raw_data_generators():
            data = data_gen(data_size)
            existing_element = random.choice(data)
            data_type = existing_element.__class__.__name__
            scores = {}
            for container in CONTAINERS:
                search_existing_element = partial(container(data).__contains__,
                                                  existing_element)
                search_missing_element = partial(container(data).__contains__,
                                                 None)
                existing_time = benchmark(search_existing_element)
                missing_time = benchmark(search_missing_element)

                scores[container] = {CSV_FIELD_ELEM: existing_time,
                                     CSV_FIELD_NONE: missing_time}

            save_scores_csv(data_size, scores, csv_writers[data_type])
    print()
