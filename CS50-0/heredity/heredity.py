import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    # people = load_data("/Users/dsparks/Github/Projects/CS50-0/heredity/data/family0.csv")
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])
    
    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def get_probability_with_parents(personData, motherGenes, fatherGenes, numGene):
    """
    Calculate the probability given what we know about the parents
    """

    # Determine the probability of having a gene for both mom and dad (with chance mutation 1%)
    motherProbability = [0.01, 0.50, 0.99][motherGenes]
    fatherProbability = [0.01, 0.50, 0.99][fatherGenes]

    # Calculate the combined probability based on the number of genes received
    if numGene == 0:
        # prob not from mom * prob not from dad
        return (1-motherProbability) * (1-fatherProbability)
    elif numGene == 1:
        # prob = prob from mom and not from dad + prob not from mom and from dad
        return motherProbability * (1-fatherProbability) + (1-motherProbability) * fatherProbability
    else:
        # prob = prob from mom * prob from dad
        return motherProbability * fatherProbability


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.
    """

    # Iterate across all people and calculate the cummulativate probability of gene and trait
    probability = 1
    for person, data in people.items():
        numGene = 1 if person in one_gene else 2 if person in two_genes else 0
        trait = person in have_trait

        # Assume either they have both parents or no parents, and if parents, determine joint probability
        if data["mother"]:
            motherGenes = 2 if data["mother"] in two_genes else 1 if data["mother"] in one_gene else 0
            fatherGenes = 2 if data["father"] in two_genes else 1 if data["father"] in one_gene else 0
            probability *= get_probability_with_parents(data, motherGenes, fatherGenes, numGene) * PROBS["trait"][numGene][trait]
        
        # No parents, just use the unconditional probability
        else:
            probability *= PROBS["gene"][numGene] * PROBS["trait"][numGene][trait]
    
    return probability


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    # For each person in probabilities...
    for person in probabilities:

        # Determine the gene count and trait
        gene_count = 1 if person in one_gene else 2 if person in two_genes else 0
        trait = True if person in have_trait else False

        # Add the pobability (passed in) to the existing total probability
        probabilities[person]["gene"][gene_count] += p
        probabilities[person]["trait"][trait] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    
    # Normalize the probabilites for each person
    for person in probabilities:
        totalGene = sum(probabilities[person]["gene"].values())
        for geneType in probabilities[person]["gene"]:
            probabilities[person]["gene"][geneType] /= totalGene
        totalTrait = sum(probabilities[person]["trait"].values())
        for traitType in probabilities[person]["trait"]:
            probabilities[person]["trait"][traitType] /= totalTrait


if __name__ == "__main__":
    main()
