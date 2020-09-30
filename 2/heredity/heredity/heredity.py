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


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    jp = 1
    namesPeople = set(people.keys())
    zero_genes = namesPeople.difference(one_gene).difference(two_genes)
    not_have_trait = namesPeople.difference(have_trait)

    def formWorld(namesPeople,zero_genes, one_gene, two_genes, have_trait, not_have_trait):
        pw  =   { 
                    person:
                        {
                            "gene"  :   None,
                            "trait" :   None 
                        }
                for person in namesPeople
        }
        # target genes
        for x in one_gene:
            pw[x]["gene"] = 1
        for x in two_genes:
            pw[x]["gene"] = 2
        for x in zero_genes:
            pw[x]["gene"] = 0
        # target traits
        for x in have_trait:
            pw[x]["trait"] = True
        for x in not_have_trait:
            pw[x]["trait"] = False
        
        return pw
    
    world = formWorld(namesPeople, zero_genes, one_gene, two_genes, have_trait, not_have_trait)

    def anyParents(person):
        if people[person]['mother'] != None and people[person]['father'] != None:
            return True
        else:
            return False

    # functions and constants for conditional case
    def genePairs(gene):
                if gene == 0:
                    return [0, 0]
                elif gene == 1:
                    return [0, 1]
                elif gene == 2:
                    return [1, 1]
                else:
                    raise ValueError('invalid gene value')
                
    def inheritGenes(motherPair, fatherPair):
        return list(itertools.product(motherPair, fatherPair))
    # list e almayi unutmustum bug burdaydi
    tableTF = list(itertools.product([True, False], [True, False]))

    def allPairs(inhGenes, tableTF):
        return list(itertools.product(inhGenes, tableTF))
    
    def mutatePairs(pairList):
        mutList = []
        for pair in pairList:
            p = 0.25 # likelihood of this inheritance / there are 4 inheritance totally
            g1 = pair[0][0]
            g2 = pair[0][1]
            # any mutation for gene 1
            if pair[1][0]:
                p *= PROBS['mutation']
                g1 = -g1 + 1
            else:
                p *= 1-PROBS['mutation']
            # any mutation for gene 2
            if pair[1][1]:
                p *= PROBS['mutation']
                g2 = -g2 + 1
            else:
                p *= 1-PROBS['mutation']
            # stored varible newGenes if mutated and probability of this gene pair's likelihood
            tmp = ((g1, g2), p)
            mutList.append(tmp)
        return mutList

    for person in namesPeople:
        # target values: gene and trait
        gene = world[person]['gene']
        trait = world[person]['trait']

        if anyParents(person):
            motherName = people[person]['mother']
            fatherName = people[person]['father']
            motherGeneCount = world[motherName]['gene']
            fatherGeneCount = world[fatherName]['gene']
            motherGenePair = genePairs(motherGeneCount)
            fatherGenePair = genePairs(fatherGeneCount)
            # due to inheritance
            crossedGenes = inheritGenes(motherGenePair, fatherGenePair)
            # consider any mutation
            rawGenePairPool = allPairs(crossedGenes, tableTF)
            # after if any mutation
            wholeGenePairPool = mutatePairs(rawGenePairPool)
            # check for the target gene count and sum the complying ones'
            childGeneProb = 0
            for p in wholeGenePairPool:
                if p[0][0]+p[0][1] == gene:
                    childGeneProb += p[1]
            jp *= childGeneProb*PROBS['trait'][gene][trait]
        else:
            jp *= PROBS['gene'][gene]*PROBS['trait'][gene][trait]

    return jp


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    namesPeople = set(probabilities.keys())
    zero_genes = namesPeople.difference(one_gene).difference(two_genes)
    not_have_trait = namesPeople.difference(have_trait)
    # update gene
    for x in zero_genes:
        probabilities[x]['gene'][0] += p
    for x in one_gene:
        probabilities[x]['gene'][1] += p
    for x in two_genes:
        probabilities[x]['gene'][2] += p
    # update trait
    for x in have_trait:
        probabilities[x]['trait'][True] += p
    for x in not_have_trait:
        probabilities[x]['trait'][False] += p



def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    namesPeople = set(probabilities.keys())
    for x in namesPeople:
        tmp = 0
        for i in range(0, 3):
            tmp += probabilities[x]['gene'][i]
        for i in range(0, 3):
            probabilities[x]['gene'][i] /= tmp
        tmp = 0
        for i in range(0, 2):
            tmp += probabilities[x]['trait'][i]
        for i in range(0, 2):
            probabilities[x]['trait'][i] /= tmp

if __name__ == "__main__":
    main()
