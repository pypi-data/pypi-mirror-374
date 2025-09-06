from build_a_bot.nlp import spacy_training
import spacy

class TestSpacyTraining:

    def test_convert_user_assistant_examples_to_docs(self):
        nlp = spacy.blank("en")
        examples = [
            {"role": "user", "content": "run on dev"},
            {"role": "assistant", "content": '{"server": "dev"}'}
        ]
        docs = spacy_training.convert_user_assistant_examples_to_docs(nlp, examples, ["server"])
        assert len(docs) == 1
        doc = docs[0]
        ents = list(doc.ents)
        assert len(ents) == 1
        assert ents[0].label_ == "server"
        assert ents[0].text == "dev"
