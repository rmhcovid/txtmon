#! /usr/bin/env python

import sys


def generate_obs(template, unique_code):
    ob_name = "ob_%s" % unique_code
    field_follower = "_%s" % unique_code

    csv = template.replace("ob_template", ob_name)
    csv = csv.replace("_template", field_follower)

    return csv


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit("Usage %s observation_template.csv" % sys.argv[0])

    obs_template = open(sys.argv[1]).read().strip()

    print(generate_obs(obs_template, "0"))
    print(generate_obs(obs_template, "1a"))
    print(generate_obs(obs_template, "1b"))
    print(generate_obs(obs_template, "2a"))
    print(generate_obs(obs_template, "2b"))
    print(generate_obs(obs_template, "3a"))
    print(generate_obs(obs_template, "3b"))
    print(generate_obs(obs_template, "4a"))
    print(generate_obs(obs_template, "4b"))
    print(generate_obs(obs_template, "5a"))
    print(generate_obs(obs_template, "5b"))
    print(generate_obs(obs_template, "6a"))
    print(generate_obs(obs_template, "6b"))
    print(generate_obs(obs_template, "7a"))
    print(generate_obs(obs_template, "7b"))
    print(generate_obs(obs_template, "8a"))
    print(generate_obs(obs_template, "8b"))
    print(generate_obs(obs_template, "9a"))
    print(generate_obs(obs_template, "9b"))
    print(generate_obs(obs_template, "10a"))
    print(generate_obs(obs_template, "10b"))
    print(generate_obs(obs_template, "11a"))
    print(generate_obs(obs_template, "11b"))
    print(generate_obs(obs_template, "12a"))
    print(generate_obs(obs_template, "12b"))
    print(generate_obs(obs_template, "13a"))
    print(generate_obs(obs_template, "13b"))
    print(generate_obs(obs_template, "14a"))
    print(generate_obs(obs_template, "14b"))
