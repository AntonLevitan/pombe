import pandas as pd
import os

DATA_DIRECTORY = "Data" + os.sep

GI = pd.read_csv("Dataset S2 - Averaged E-MAP one allele per gene.csv", header=None)
GS = pd.read_csv("Dataset S3 - S.pombe Similarity Scores.csv", header=None)

output_name_GI = "gene_interactions"
output_name_GS = "gene_similarity"
output_name_combined = "GI_and_GS"

output_file_suffix = ".csv"

column_a = "Gene A"
column_b = "Gene B"

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
        combined.columns = [column_a, column_b, output_name]
        combined = combined.dropna()
        combined.to_csv(DATA_DIRECTORY + output_name + output_file_suffix, index=False)
        return combined


def combine_features(data1, data2, output_name):

        data = data1.merge(data2, on=[column_a, column_b])
        data.to_csv(DATA_DIRECTORY + output_name + output_file_suffix, index=False)

        return data


GI_transformed = mxn_to_list(GI, output_name_GI)
GS_transformed = mxn_to_list(GS, output_name_GS)

combined = combine_features(GI_transformed, GS_transformed, 'combined')

