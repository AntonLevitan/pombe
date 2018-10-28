import pandas as pd
import os

DATA_DIRECTORY = "Data" + os.sep

data = pd.read_csv("Dataset S2 - Averaged E-MAP one allele per gene.csv", header=None)
# data = pd.read_csv("Dataset S3 - S.pombe Similarity Scores.csv", header=None)

output_file_name = "gene_interactions"
# output_file_name = "gene_similarity"

output_file_suffix = ".csv"


def mxn_to_list(data, output_name):

        score = data.iloc[:, 1:].values.flatten()
        score = score[len(data.iloc[0])-1:]
        score = pd.DataFrame(score)

        gene_a = []
        gene_b = []

        for i in data.iloc[1:, 0]:
                for j in range(1, len(data.iloc[0])):
                        gene_b.append(data.iloc[0, j])
                        gene_a.append(i)

        gene_a = pd.DataFrame(gene_a)
        gene_b = pd.DataFrame(gene_b)
        frames = [gene_a, gene_b, score]

        combined = pd.concat(frames, axis=1)
        combined.columns = ["Gene A", "Gene B", output_file_name]

        combined.to_csv(DATA_DIRECTORY + output_name + output_file_suffix)


if __name__ == "__main__":
    mxn_to_list(data, output_file_name)
