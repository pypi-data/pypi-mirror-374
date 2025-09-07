from functools import lru_cache
from edn_format import Keyword
from shadowprover.reasoners.planner_meta import encode_plan
from shadowprover.reasoners.utils import complete, get_ground_instances
from ..syntax.reader import r
from ..syntax.expression import *
from ..fol.fol_prover import *
from ..syntax.reader import *

from .shadow_prover import *
from ..unifiers.first_order_unify import *
from edn_format import Keyword
from ..syntax.expression import *
from edn_format import Keyword
from ..syntax.expression import *

name_keyword = Keyword("name")
description_keyword = Keyword("description")
assumptions_keyword = Keyword("assumptions")
goal_keyword = Keyword("goal")
schema_keyword = Keyword("schema")
name_keyword = Keyword("name")

inputs_keyword = Keyword("inputs")
output_keyword = Keyword("output")

from PIL import Image, ImageDraw
from IPython.display import clear_output

img = Image.new('RGB', (300, 300), 'white')
draw = ImageDraw.Draw(img)

draw.rectangle([50, 50, 150, 100], outline='black', fill='lightblue')
draw.rectangle([160, 160, 250, 240], outline='black', fill='orange')


    
class Action:
    def __init__(self, predicate,  precondition, additions, deletions, postconditions=None):
        self.predicate = predicate
        self.precondition = precondition
        self.postconditions = postconditions
        self.additions = set(additions)
        self.deletions = set(deletions)
        self.variables = list(map(str, predicate.args))

    def __existentially_quantified__(self, expr):
        return r(f"(exists [{' '.join(map(str, self.predicate.args))}] {str(expr)})")

    def __universally_quantified__(self, expr):
        
        return r(f"(forall [{' '.join(map(str, expr.args))}]  {str(expr)})")

    
    def applicable(self, domain, background, state, prover, max_answers, completions):
        existential = self.__existentially_quantified__(self.precondition)
        full_state = background.union(state)
        
        completion_formula = self.generate_completion(completions, state)
        answers = is_satisfied_with_matches(full_state | completion_formula, existential, prover, max_answers)
        
        if not answers:
            return None
        if not self.postconditions:
            return answers
        else:
            answers_matching_postcondition = []
            if type(answers)==list:
                for answer in sort_substitutions(answers, state):
                    changes = self.apply(state, answer)
                    new_full_state = background.union(changes['new_state'])
                    
                    completion_formula = self.generate_completion(completions, new_full_state)
                    
                    all_ok = all([prover(set(filter(lambda x:not(x.is_modal() and 'attention' in x.modal_type),  new_full_state | completion_formula)), postcondition.apply_substitution(answer))[0] for postcondition in self.postconditions])
                    if all_ok:
                        answers_matching_postcondition.append(answer)
            if len(answers_matching_postcondition) > 0:
                return answers_matching_postcondition
            else:
                return None

    def generate_completion(self, completions, new_full_state):
        completion_formulae = set()
        for completion in completions:
            ground_instances = get_ground_instances(Symbol(completion), new_full_state)
            if ground_instances:
                completion_formulae  = completion_formulae | {complete(ground_instances)}
        return completion_formulae
                        
            

    def apply(self,  state, theta):
        deletions = set([d.apply_substitution(theta) for d in self.deletions])
        additions = set([a.apply_substitution(theta) for a in self.additions])
        
        new_state = (state - deletions) | additions
        return {"new_state":  new_state, "additions": additions, "deletions": deletions}
    
    def __str__(self):
        return self.predicate
  


def is_satisfied_with_matches(state, test, prover, max_answers):
    try:
        (satisfied, proof, answers) = prover(set(filter(lambda x:not(x.is_modal() and 'attention' in x.modal_type),  state)), test, find_answer=True, max_answers=max_answers)
    
        if satisfied:

            
            return answers if answers else True
        else:
            return None
    except Exception as e:
        print(str(e))


def plan2(domain, background, current_state, goal, actions, prover=fol_prove, completions=[], visited=None, changes_so_far =[]):



    match = is_satisfied_with_matches(current_state, goal, prover, max_answers=len(domain))
    
    if match == True:
        return []  

    if not visited:
        visited = set([frozenset(current_state)])
    
    for action in actions:
        matching_substitutions = action.applicable(domain, background, current_state, prover, max_answers=len(domain), completions=completions)
        if type(matching_substitutions)==list:

            for matching_substitution in matching_substitutions:
                changes = action.apply(current_state, matching_substitution)
                new_state = changes["new_state"]
                additions = changes["additions"]
                deletions = changes["deletions"]
                del changes['new_state']

                if frozenset(new_state) not in visited:
                    for change in changes_so_far:
                        if change["additions"] == deletions and change["deletions"] == additions:
                            return False
                    from_here = plan2(domain, background, new_state, goal, actions, prover,
                                      visited.union(set([frozenset(new_state)])), changes_so_far + [changes])
                    if from_here is not False:
                        return [action.predicate.apply_substitution(matching_substitution)]+from_here
                        

    return False   


def compute_similarity(a, b)-> float:
    #if other == syntax.reader.r('(if H (not Ma))') and is_atomic(self):
        #return -1000000
        
    x = fol_reify(a).get_sub_expressions()
    y = fol_reify(b).get_sub_expressions()
    d = max(len(x), len(y)) 
    if d == 0:
        return 0
    return len(set(x).intersection(y))/d

def sort_actions(actions, state, goal):
    attention_modals = set(map(lambda x: x.kernel, set(filter(lambda x: is_modal(x) and x.modal_type=="attention", state))))

    if attention_modals:
        actions =  list(sorted(actions, key=lambda action: -max(map(lambda x: compute_similarity(action.predicate, x), attention_modals))))
        
    else:
        actions =  list(sorted(actions, key=lambda action: -max(map(lambda x: compute_similarity(goal, x), action.additions))))
    return actions

def sort_substitutions(substitutions, state):
    attention_modals = set(map(lambda x: x.kernel, set(filter(lambda x: is_modal(x) and x.modal_type=="attention-obj", state))))

    if attention_modals:
        return  sorted(substitutions, key=lambda sub: -sum(max(map(lambda x: 1 if v==x else 0, attention_modals)) for v in sub.values()))
    else:
        return substitutions

def prune_actions(actions, goal):
    relevant_actions = set(filter(lambda action : max([ compute_similarity(goal,p) for p   in action.additions]) > 0, actions))
    
    remaining = set(actions).difference(relevant_actions)
    
    while remaining:
        current_relevant = set()
        for relevant_action in relevant_actions:
            current_relevant = current_relevant.union(set(filter(lambda action : max([compute_similarity(relevant_action.precondition,p) for p   in action.additions])>0, remaining)))
        relevant_actions = relevant_actions.union(current_relevant)
        remaining_this_round = set(remaining).difference(relevant_actions)
        if len(remaining) == len(remaining_this_round):
            return relevant_actions
        else:
            remaining = remaining_this_round
    return relevant_actions

def inertia_function(background, state, goal, prover):
    updated_state = state.copy()
    for relevant_item in filter(lambda x: x.is_modal(), set(goal.sub_formulae) - {goal}): 
        negated_relevant_item = negated(relevant_item)
        proved_r =  prover(background | state - {relevant_item}, relevant_item ) ## does the belief still hold
        if not proved_r:
            proved_not_r= prover(background | state - {negated_relevant_item}, negated_relevant_item)
        else:
            proved_not_r = False
    
        if proved_r:
            updated_state =  (state  | {relevant_item}) - {negated_relevant_item}
        if proved_not_r:
            updated_state = (state | {negated_relevant_item}) - {relevant_item}
    return updated_state 

from functools import wraps
from typing import Callable, Set, TypeVar, Dict, Tuple, FrozenSet

T = TypeVar('T')
U = TypeVar('U')

def monotonic_cache(func: Callable[[Set[T], U], bool]) -> Callable[[Set[T], U], bool]:
    false_cache: Dict[U, Set[FrozenSet[T]]] = {}  # arg2 -> set of frozensets (False results)
    true_cache: Dict[U, Set[FrozenSet[T]]] = {}   # arg2 -> set of minimal frozensets (True results)

    @wraps(func)
    def wrapper(arg1: Set[T], arg2: U) -> bool:
        f_arg1 = frozenset(arg1)

        # ✅ Check for known True via subset
        for superset in true_cache.get(arg2, set()):
            if superset.issubset(f_arg1):
                return True

        # ❌ Check for known False via superset
        for subset in false_cache.get(arg2, set()):
            if f_arg1.issubset(subset):
                return False

        # Evaluate actual function
        result = func(arg1, arg2)

        if result:
            # Remove any supersets from true_cache (we only keep minimal True sets)
            true_sets = true_cache.setdefault(arg2, set())
            to_remove = {s for s in true_sets if f_arg1.issubset(s)}
            true_sets.difference_update(to_remove)
            true_sets.add(f_arg1)
        else:
            # Only store the False result
            false_cache.setdefault(arg2, set()).add(f_arg1)

        return result

    return wrapper

def planbfs(domain, 
            background, 
            start_state, 
            goal, actions, 
            prover=fol_prove, 
            transition_fn=lambda x,y,z: y, 
            completions={}, 
            meta_conditions=False, 
            follow_along_plan=[], 
            verification_mode=False,
            verbose=False,
            visualizer=None):

    Q =  []
    Q.append((start_state, [], [start_state]))    
    explored = set([frozenset(start_state.union(background))])
    actions = prune_actions(actions, goal)
    @lru_cache(maxsize=None)
    def fol_prove_cache(inputs, output):
        return fol_prove(inputs, output)
    @monotonic_cache
    def sst_prove(inputs, output):
        return prover(inputs, output)[0]
    
    while Q:
        v, path, sequence = Q.pop(0)
        v = inertia_function(background, v, goal, sst_prove)                            
        match = is_satisfied_with_matches(background | v , goal, prover, max_answers=len(domain))
        
        if visualizer:
            print("------")
            clear_output(wait=True)
            visualizer(v, path, match, {"path_length": len(path), "explored": len(explored)})
        if match:
            # v = inertia_function(background, new_state, goal, sst_prove)  
            return path, v, len(explored), sequence
 
        for action in sort_actions(filter(lambda a: not verification_mode or (len(follow_along_plan) > len(path) and a.predicate.head == (follow_along_plan[len(path)]).head), actions), v, goal):

            if not meta_conditions or not fol_prove_cache(frozenset(encode_plan(path) | meta_conditions | { r(f"(Next {action.predicate.head})")}), r("False"))[0]:

                matching_substitutions = action.applicable(domain, background, v, prover, max_answers=10, completions=completions)
                if type(matching_substitutions)==list:
                    for matching_substitution in sort_substitutions(matching_substitutions, v):
                        changes = action.apply(v, matching_substitution)
                        new_state = frozenset(changes["new_state"])
                        #new_state = inertia_function(background, new_state, goal, sst_prove)                            
                        
                        if new_state not in explored: 
                            explored.add(new_state)
                            # check meta constraints and then add
                            next_step = action.predicate.apply_substitution(matching_substitution)
                            ## check if next_step matches partial plan
                            if follow_along_plan and len(follow_along_plan) > len(path):
                                follow_along_plan_step = follow_along_plan[len(path)]
                                if next_step == follow_along_plan_step:
                                    Q.append((new_state, path + [next_step], sequence + [new_state]))
                            else:
                                if not verification_mode:
                                    Q.append((new_state, path + [next_step], sequence + [new_state]))
                                else:
                                    return False
                            
                                    

    return None, None, len(explored), None   


def cached_prover(prover):
    @cache
    def cached_prover(state, test, find_answer=True, max_answers=5):
        return prover(state, test, find_answer=True, max_answers=max_answers)
    
    def _prover_(state, test, find_answer=True, max_answers=5):
        return cached_prover(frozenset(state), test, find_answer=True, max_answers=max_answers)
    
    return _prover_

def verify_plan(plan, domain, background, start_state, goal, actions, prover=fol_prove, transition_fn=lambda x,y,z:y, completions={}, meta_conditions={}, verbose=False):
    return planbfs(domain, background, start_state, goal, actions, prover, completions=completions, meta_conditions=meta_conditions, transition_fn=transition_fn, follow_along_plan=plan, verification_mode=True, verbose=verbose) 


def run_spectra(domain, background, start_state, goal, actions, prover=fol_prove, transition_fn=lambda x,y,z:y, completions={}, meta_conditions={}, follow_along_plan=[], verification_mode=False, decompose_goal=False, verbose=False, visualizer=None):
    
    if is_and(goal) and decompose_goal:
        conjuncts = goal.args
        plan = []
        new_state = start_state
        num_explored_total = 0
        for conjunct in conjuncts:
            partial_plan, new_state, num_explored = planbfs(domain, background, new_state, conjunct, actions, prover=cached_prover(prover), transition_fn=transition_fn)
            num_explored = num_explored_total + num_explored 
            if partial_plan is None:
                return None
            else:
                plan += partial_plan 
        return plan
    return planbfs(domain, background, start_state, goal, actions, prover=cached_prover(prover), completions=completions, meta_conditions=meta_conditions, transition_fn=transition_fn, follow_along_plan=follow_along_plan, verification_mode=verification_mode, verbose=verbose,visualizer=visualizer)
