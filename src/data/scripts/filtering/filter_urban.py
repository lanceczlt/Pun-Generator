import csv
import os

with open('urbandict-words.csv') as csvfile:
    reader = csv.reader(csvfile)

    with open('new_urbandict-words.csv', 'w', newline='') as newfile:
        writer = csv.writer(newfile)

        for row in reader:
            words = row[0].split()

            # Check if there are 2 or more words
            if len(words) >= 2:
                writer.writerow(row)

os.replace('new_urbandict-words.csv', 'urbandict-words.csv')
