from deepllm.recursors import *


class Advisor(AndOrExplorer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        pname = advisor_oracle["name"]
        oname = f"{self.name}_{pname}"
        self.oracle = Agent(name=oname)
        self.oracle.set_pattern(advisor_oracle["decider_p"])

    def appraise(self, g, _trace):
        # xs = to_list((g, trace))
        # context = ", ".join(xs)

        advice = just_ask(self.oracle, g=g, context=self.initiator)

        tprint("!!! ADVICE for:", g, advice)

        return advice.startswith("True")

    def resume(self):
        super().resume()
        self.oracle.resume()

    def persist(self):
        super().persist()
        self.oracle.persist()

    def costs(self):
        d = super().costs()
        d["oracle"] = self.oracle.dollar_cost()
        return d


class Rater(AndOrExplorer):
    def __init__(self, threshold=None, **kwargs):
        super().__init__(**kwargs)
        pname = rater_oracle["name"]
        oname = f"{self.name}_{pname}"
        self.oracle = Agent(oname)
        self.oracle.set_pattern(rater_oracle["rater_p"])
        self.threshold = threshold

    def appraise(self, g, _trace):

        advice = ask_for_clean(self.oracle, g=g, context=self.initiator)

        if not advice:
            tprint("*** NO ADVICE FOR:", g)
            return False

        rating = advice[0].strip()

        tprint(f"\n-----EXPLANATION {rating}\n---\n")
        rating = rating.split("|")[0].strip()
        if " " in rating:
            rating = rating.split()[1]
        try:
            f = float(rating)
        except Exception:
            print("*** UNPARSED RATING:", advice)
            f = 5
        f = f / 100.0

        ok = f >= self.threshold

        tprint(f'RATING of "{g}" w.r.t "{self.initiator}" is {round(f, 4)} --> {ok}')

        return ok

    def resume(self):
        super().resume()
        self.oracle.resume()

    def persist(self):
        super().persist()
        self.oracle.persist()

    def costs(self):
        d = super().costs()
        d["oracle"] = self.oracle.dollar_cost()
        return d


class AbstractMaker:
    def __init__(self, topic=None, keywords=None):
        assert None not in (topic, keywords)
        self.topic = " ".join(topic.strip().split())
        self.keywords = keywords
        prompter = sci_abstract_maker
        pname = prompter["name"]
        tname = topic.replace(" ", "_").lower()
        self.agent = Agent(f"{tname}_{pname}")
        self.agent.set_pattern(prompter["writer_p"])
        PARAMS()(self)

    def clear(self):
        self.agent.clear()

    def dollar_cost(self):
        return self.agent.dollar_cost()

    def run(self):
        return ask_for_clean(self.agent, g=self.topic, context=self.keywords)


class SummaryMaker:
    def __init__(self, text, sum_size=8, kwd_count=6, tname=None, cache=True):
        self.text = text
        self.sum_size = sum_size
        self.kwd_count = kwd_count
        self.cache = cache
        prompter = summary_maker
        pname = prompter["name"]
        if tname is None:
            tname = text[0:20].replace(" ", "_")
        self.agent = Agent(f"{tname}_{pname}")
        self.agent.set_pattern(prompter["sum_p"])
        PARAMS()(self)
        if self.cache:
            self.agent.resume()

    def clear(self):
        self.agent.clear()

    def dollar_cost(self):
        return self.agent.dollar_cost()

    def run(self):
        answer = self.agent.ask(
            text=self.text, sum_size=self.sum_size, kwd_count=self.kwd_count
        )
        if self.cache:
            self.agent.persist()
        print("\n\nANSWER:----------\n")
        print(answer)
        print("------\n\n")
        return str(answer)


class PaperReviewer:
    def __init__(self, text, tname=None, cache=True):
        self.text = text
        self.cache = cache
        prompter = paper_reviewer
        pname = prompter["name"]
        if tname is None:
            tname = text[0:20].replace(" ", "_")
        self.agent = Agent(f"{tname}_{pname}")
        self.agent.set_pattern(prompter["rev_p"])
        PARAMS()(self)
        if self.cache:
            self.agent.resume()

    def clear(self):
        self.agent.clear()

    def dollar_cost(self):
        return self.agent.dollar_cost()

    def run(self):
        answer = self.agent.ask(
            text=self.text,
        )
        if self.cache:
            self.agent.persist()
        return str(answer)


class RetrievalRefiner:
    def __init__(self, text, quest, tname=None, cache=True):
        self.text = text
        self.quest = quest
        self.cache = cache
        prompter = retrieval_refiner
        pname = prompter["name"]
        if tname is None:
            tname = text[0:20].replace(" ", "_")
        self.agent = Agent(f"{tname}_{pname}")
        self.agent.set_pattern(prompter["rev_p"])
        PARAMS()(self)
        if self.cache:
            self.agent.resume()

    def clear(self):
        self.agent.clear()

    def dollar_cost(self):
        return self.agent.dollar_cost()

    def run(self):
        answer = self.agent.ask(text=self.text, quest=self.quest)
        if self.cache:
            self.agent.persist()
        return str(answer)
