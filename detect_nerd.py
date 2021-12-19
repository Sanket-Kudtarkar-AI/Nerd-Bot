import re
import spacy
import wordtodigits
from nltk.tokenize import word_tokenize
import json

# Category dictionary where keys are category name and values are the entities.
with open("DATA/category_dict.json", "r",
          encoding='utf-8') as fp:
    category_dict = json.load(fp)


# Main class which contains all the methods
class DetectNerd:
    def __init__(self, nlp_amount, nlp_nil, nlp_quantity):
        self.nlp_amount = nlp_amount
        self.nlp_nil = nlp_nil
        self.nlp_quantity = nlp_quantity

    # Function which returns amount
    def detect_amount(self, input_text):
        """
        :param input_text: string
        :return: one element list
        """
        doc = self.nlp_amount(input_text)
        try:
            if doc.ents:
                # ignore the for loop
                for _ent in doc.ents:
                    return [_ent.text]
            else:
                return [0]
        except (Exception,):
            return [0]

    # Utility function which identifies the category entities returns [Nil] if none present
    def detect_nil(self, input_text):
        """
        :param input_text: string
        :return: list
        """
        doc = self.nlp_nil(input_text)
        entities_list = []
        if doc.ents:
            for _ent in doc.ents:
                entities_list.append(_ent.text)
            return entities_list
        else:
            return ['Nil']

    # V2
    def detect_category(self, input_text):
        """
        :param input_text: string
        :return: dictionary of categories and entities
        """
        ex_text = input_text.lower()
        ex_text_tokenized = word_tokenize(ex_text)
        categories_detect_dict = {"clothing_fashion": [],
                                  "food_beverages": [],
                                  "expenses": [],
                                  "entertainment": [],
                                  "fuel": [],
                                  "gadgets_appliances": [],
                                  "gifts_stationery": [],
                                  "grocery": [],
                                  "health_beauty": [],
                                  "home_furnish": [],
                                  "miscellaneous": [],
                                  "online_shopping": [],
                                  "spa_salon": [],
                                  "travel_hotels": [],
                                  "vehicle": [],
                                  "errands": []}

        found = False

        for category, entities_list in category_dict.items():

            for entity in entities_list:
                entity = entity.strip()
                if len(entity.split(" ")) == 1:
                    word_to_find_1 = entity
                    if word_to_find_1 in ex_text_tokenized:
                        found = True
                        categories_detect_dict[category].append(word_to_find_1)
                else:
                    word_to_find_2 = entity
                    word_to_find_2 = word_to_find_2.lower()
                    if word_to_find_2 in ex_text:
                        found = True
                        categories_detect_dict[category].append(word_to_find_2)

        for cat, extracted_entity in categories_detect_dict.items():
            to_be_removed = []
            for entity_i in categories_detect_dict[cat]:
                for entity_j in categories_detect_dict[cat]:
                    if (entity_i != entity_j) and (entity_i in entity_j):

                        if entity_i in categories_detect_dict[cat]:
                            to_be_removed.append(entity_i)

            categories_detect_dict[cat] = [x for x in categories_detect_dict[cat] if x not in to_be_removed]

            to_be_removed = []

            for word in word_tokenize(" ".join(categories_detect_dict[cat])):
                if word not in ex_text_tokenized:
                    to_be_removed.append(word)
            categories_detect_dict[cat] = [x for x in categories_detect_dict[cat] if x not in to_be_removed]

        if found:
            # Only show the detected categories in final dictionary
            op = {k: v for k, v in categories_detect_dict.items() if v}

            # if ('grocery' in op) and ('online_shopping' in op):
            #     op['grocery'] = []

            # print(f"len(op) == {len(op)}")
            # print(f"op == {op}")

            if (len(op) > 1) and ('online_shopping' in op):
                # print("yes")
                op['online_shopping'] = []
                # op['home_furnish'] = []
                # op['clothing_fashion'] = []
                # op['gadgets_appliances'] = []
                # op['health_beauty'] = []
                # op['home_furnish'] = []
                # op['grocery'] = []
                # op['grocery'] = []
                # op['grocery'] = []

            op = {k: v for k, v in op.items() if v}

            if op:
                return op
            else:
                if self.detect_nil(input_text) == ['Nil']:
                    return {'nil': []}

                else:
                    return {'others': []}

        else:
            if self.detect_nil(input_text) == ['Nil']:
                return {'nil': []}

            else:
                return {'others': []}

    def detect_quantity(self, input_text):
        """
        :param input_text: string
        :return: All the numbers
        :rtype: list
        """
        input_text = input_text.strip()
        doc = self.nlp_quantity(input_text)
        entities_list = []
        if doc.ents:
            for _ent in doc.ents:
                if _ent.label_ == 'CARDINAL':
                    entities_list.append(_ent.text)
            return entities_list
        else:
            return None

    def detect_cat_amount(self, input_text):
        """
        :param input_text: string
        :return: {"amount": amount,
                  "category": category,
                  "quantities": quantities,
                  "multiplier": quantities}
        :rtype: dict
        """
        input_text_split_and = input_text.split(" and ")
        input_text_split_comma = []

        for i in input_text_split_and:
            for comma in i.split(","):
                input_text_split_comma.append(comma)

        main_dict = {}
        contexts = 0

        for text in input_text_split_comma:

            token = word_tokenize(text)

            try:
                if token[-1] == ".":
                    token.pop(-1)
                text = " ".join(token)
            except (Exception,):
                pass
            text_tokenized = word_tokenize(text)
            contexts += 1
            text = text.strip()

            amount = self.detect_amount(text)

            category = self.detect_category(text)
            quantities = self.detect_quantity(text)

            multiplier_words = ['per', 'each', 'apiece']

            is_multiplier = False
            for token in text_tokenized:
                if token in multiplier_words:
                    is_multiplier = True

            '''if the text contains words like "per" and "each" then the quantity would be multiplied with the amount
            so I'm adding multiplier object in main_dict[context] else no multiplier object'''

            if is_multiplier:
                if quantities:
                    main_dict[f"context_{contexts}"] = {"amount": amount,
                                                        "category": category,
                                                        "quantities": quantities,
                                                        "multiplier": quantities}
                else:

                    main_dict[f"context_{contexts}"] = {"amount": amount,
                                                        "category": category,
                                                        "quantities": [1],
                                                        "multiplier": [1]}

            else:

                main_dict[f"context_{contexts}"] = {"amount": amount,
                                                    "category": category,
                                                    "quantities": quantities,
                                                    "multiplier": [1]}

            for context in main_dict.keys():

                if (main_dict[context]['amount'] is not None) & (main_dict[context]['quantities'] is not None):
                    for i in main_dict[context]['amount']:
                        if i in main_dict[context]['quantities']:
                            main_dict[context]['quantities'].remove(i)

        return main_dict

    def detect(self, input_text):
        """
        :param input_text: string
        :return: {"amount": amount,
                  "category": category,
                  "quantities": quantities,
                  "multiplier": quantities}
        :rtype: dict
        """
        input_text = input_text.replace("-", " ")
        
        #     input_text = 'A grocery bill for 12000rs.'
        corrected_dict = {}
        found_words_list = re.findall("\d+,\d+", input_text) + \
                           re.findall("\d+rs", input_text) + \
                           re.findall("\d+Rs", input_text) + \
                           re.findall("a hundred", input_text) + \
                           re.findall("a thousand", input_text) + \
                           re.findall("hundred and", input_text) + \
                           re.findall("dollars", input_text)

        if found_words_list:
            for found_words in found_words_list:
                corrected_dict[found_words] = found_words.replace(",", "")
                input_text = input_text.replace(found_words, found_words.replace(",", ""))
                input_text = input_text.replace(found_words, found_words.replace("rs", ""))
                input_text = input_text.replace(found_words, found_words.replace("Rs", ""))
                input_text = input_text.replace(found_words, found_words.replace("a hundred", "one hundred"))
                input_text = input_text.replace(found_words, found_words.replace("a thousand", "one thousand"))
                input_text = input_text.replace(found_words, found_words.replace("hundred and", "hundred"))
                input_text = input_text.replace(found_words, found_words.replace("dollars", ""))

        input_text = input_text.replace("half a thousand", "500")
        input_text = input_text.replace("a couple of hundred", "200")
        input_text = input_text.replace("and a half thousand", "thousand five hundred")

        #     input_text = input_text.replace("grand","thousand")

        cat_total = {}
        # print(input_text)
        detect_cat_amount_op_dict = self.detect_cat_amount(input_text=input_text)
        for keys, values in detect_cat_amount_op_dict.items():
            total = 0

            if detect_cat_amount_op_dict[keys]['category']:
                detected_cat = list(detect_cat_amount_op_dict[keys]['category'].keys())[0]
            else:
                detected_cat = 'other'

            if detected_cat not in cat_total:
                cat_total[detected_cat] = 0

            if detect_cat_amount_op_dict[keys]['amount'] is not None:

                # amount preprocessing
                try:

                    amount = int(detect_cat_amount_op_dict[keys]['amount'][0])

                except (Exception,):

                    amount = detect_cat_amount_op_dict[keys]['amount'][0].replace('rs', '')

                    amount = amount.replace('RS', '')
                    amount = amount.replace('Rs', '')
                    if ('K' in amount) or \
                            ('k' in amount) or \
                            ('grand' in amount):

                        amount = amount.replace('K', '')
                        amount = amount.replace('k', '')
                        amount = amount.replace('grand', '')

                        amount = wordtodigits.convert(amount)
                        amount = re.sub("[^\d]", "", amount)
                        amount = amount.strip()
                        try:
                            amount = int(amount) * 1000
                        except (Exception,):
                            amount = 0
                    elif ('laks' in amount) or \
                            ('lakhs' in amount) or \
                            ('lakh' in amount):
                        print("Yes")
                        amount = amount.replace('laks', '')
                        amount = amount.replace('lakhs', '')
                        amount = amount.replace('lakh', '')

                        amount = wordtodigits.convert(amount)
                        amount = re.sub("[^\d]", "", amount)
                        amount = amount.strip()

                        try:
                            amount = int(amount) * 100000
                        except (Exception,):
                            amount = 0

                    else:
                        amount = wordtodigits.convert(amount)
                        amount = amount.strip()

                        try:
                            amount = int(amount)
                        except (Exception,):
                            amount = 0

                if detect_cat_amount_op_dict[keys]['multiplier']:
                    if type(detect_cat_amount_op_dict[keys]['multiplier'][0]) == str:
                        try:
                            multiplier = int(wordtodigits.convert(detect_cat_amount_op_dict[keys]['multiplier'][0]))
                        except (Exception,):
                            multiplier = 0

                    else:
                        multiplier = int(detect_cat_amount_op_dict[keys]['multiplier'][0])

                else:
                    multiplier = 1
                total = amount * multiplier
            #

            cat_total[detected_cat] += total

        # final_dictionary for output
        final_record_dictionary = {}

        if ('grocery' in cat_total) and ('online_shopping' in cat_total):
            del cat_total['online_shopping']

        for final_category, final_amount in cat_total.items():
            final_record_dictionary[final_category] = final_amount

        return {'amounts': list(final_record_dictionary.values()),
                'categories': list(final_record_dictionary.keys())}

    def process_op(self, input_text):
        input_dict = self.detect(input_text)
        am_list = input_dict['amounts']
        cat_list = input_dict['categories']
        new_am_list = []
        new_cat_list = []

        if 0 in am_list and 'nil' in cat_list:
            am_list.remove(0)
            cat_list.remove('nil')

        if 0 in am_list and 'others' in cat_list:
            am_list.remove(0)
            cat_list.remove('others')

        for i in range(len(cat_list)):
            new_am_list.append(am_list[i])
            new_cat_list.append(cat_list[i])

        return {'amounts': new_am_list, 'categories': new_cat_list}


if __name__ == "__main__":
    # pass
    nlp_amount = spacy.load('models/spacy_amount_md_2')
    nlp_nil = spacy.load('models/spacy_nil')
    nlp_quantity = spacy.load('models/spacy_quantities')

    dn = DetectNerd(nlp_amount, nlp_nil, nlp_quantity)
    # print(dn.detect("m ready to travel... just pulled my ticket for 5000 to book a flight"))
    # print(dn.detect_cat_amount("m ready to travel... just pulled my ticket for 5000 to book a flight"))
    # print(dn.detect("Yesterday I splashed out on groceries for 1,500"))
    print(dn.detect("i blew away 1,500 pieces of clothing from amazon"))
