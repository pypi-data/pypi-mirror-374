from typing import List
from typing import Optional
from dataclasses import dataclass
import edn_format
from edn_format import Symbol, loads

from .modal import get_modal_expression_type



def read_symbol_or_symbols(expr, is_top=False):
    if type(expr) == edn_format.edn_lex.Symbol:
        return Expression(Symbol(str(expr)), is_top=is_top)

    head, *rest = expr
    return Expression(
        edn_format.Symbol(str(head)),
        list(map(read_symbol_or_symbols, rest)),
        is_top=is_top,
    )

def r(formula_str):
    return read_symbol_or_symbols(edn_format.loads(formula_str), is_top=True)
    
EXTENSIONAL_COMPOUNDS = list(map(Symbol, [
    "not", "if", "iff", "or", "and", "forall", "exists"
]))

@dataclass
class Expression():
    head: Symbol
    args: Optional[List["Expression"]] = None
    modal: bool = False
    modal_type: str = None
    agent: "Expression" = None
    time: "Expression" = None
    kernel: "Expression" = None
    is_top: bool = False
    is_compound: bool = False
    is_schema: bool=False
    
    


    #__match_args__ = ("head", )

    def __init__(self,
                 head: Symbol,
                 args: Optional[List["Expression"]] = None,
                 is_top: bool = False,
                 is_schema: bool = False):
        self.head = head
        modal_def = get_modal_expression_type(head)
        self.is_top = is_top
        self.is_compound = self.head in EXTENSIONAL_COMPOUNDS
        if modal_def:
            self.modal = True
            self.modal_type = modal_def.modal_type
            if modal_def.has_agent:
                self.agent = args[0]
                if len(args) > modal_def.min_args:
                    self.time = args[1]
                else:
                    self.time = Expression(loads("now"))
            else:
                if len(args) > modal_def.min_args:
                    self.time = args[0]
                else:
                    self.time = Expression(loads("now"))
            self.kernel = args[-1]
        if args:
            self.args = args
        else:
            self.args = None  ## set [] to None
        self.sub_expressions = self._get_sub_expressions_()
        self.sub_formulae = self._get_sub_formulae_()
        if is_quantifier(self):
            self.kernel = args[-1]
        if not args:
            
            self.level = 0 
        else:
            if is_quantifier(self):
                self.level = 1 
            if is_modal(self):
                self.level = 2
            else:
                self.level = max(map(lambda x: x.level, args))

    def __repr__(self):
        if not self.args:
            return str(self.head)
        return f"({str(self.head)} {' '.join(map(repr, self.args))})"

    def convert_to_schema(self):
        self.is_schema = True
        return self
        
    def is_atomic(self) -> bool:
        return not self.args or len(self.args) == 0
    def is_predicate(self) -> bool:
        return self.is_atomic() or (not self.is_compound and not self.is_modal())

    def is_variable(self):
        return self.is_atomic() and (str(self).endswith("?")
                                     or str(self).startswith("?"))

    def is_modal(self) -> bool:
        return self.modal

    def get_modal_type(self) -> str:
        return self.modal_type

    def get_agent(self) -> "Expression":
        if self.modal and self.agent:
            return self.agent
        if not self.modal:
            raise Exception(f"{self} is not modal")
        if not self.agent:
            raise Exception(f"{self} does not have an agent")

    def get_time(self) -> "Expression":
        return self.time
    
    def get_local_context(self):
        if self.is_modal():
            return Expression(loads("context"),list(map(lambda x: Expression(loads(x), is_top=False), [self.get_modal_type().replace("-",""), str(self.agent or 'all'),str(self.time) ])))
            #key = str(self.get_modal_type()) + str(self.agent) + str(self.time)
            #return Expression(loads(key), [], is_top=True)
        else:
            return Expression(loads("context"), [loads("end")])

    def get_kernel(self) -> "Expression":
        return self.kernel

    def _get_sub_expressions_(self) -> List["Expression"]:
        return [self,# Expression(self.head)
                ] + sum(
            map(Expression.get_sub_expressions, self.args or []), [])

    def get_sub_expressions(self) -> List["Expression"]:
        return self.sub_expressions

    #TODO: store as object var
    def _get_sub_formulae_(self) -> List["Expression"]:
        sub_formulae = []
        if self.is_top:
            sub_formulae = sub_formulae + [self]

        if self.is_compound:
            for arg in self.args:
                sub_formulae = sub_formulae + [arg] + arg.get_sub_formulae()

        if self.modal:
            sub_formulae = sub_formulae + [self.kernel
                                           ] + self.kernel.get_sub_formulae()

        return sub_formulae

    def get_sub_formulae(self) -> List["Expression"]:
        return self.sub_formulae

    def get_constants(self) -> List["Expression"]:
        return set(
            list(
                filter(lambda x: x.is_atomic() and not x.is_variable(),
                       self.get_sub_expressions())))

    def get_all_variables(self) -> List["Expression"]:
        return set(
            list(
                filter(lambda x: x.is_atomic() and x.is_variable(),
                       self.get_sub_expressions())))

    def __eq__(self, other):
        if not other:
            print(self)
            
        if not self.head == other.head:
            return False
        if not self.args and other.args:
            return False
        if self.args and not other.args:
            return False

        if not self.args and not other.args:
            return True

        return len(self.args) == len(other.args) and all(
            map(lambda x, y: x == y, self.args, other.args))

    def apply_substitution(self, theta) -> "Expression":
        if self in theta:
            return theta[self]
        return Expression(
            self.head,
            list(
                map(lambda arg: arg.apply_substitution(theta), self.args
                    or [])))
        
    def compute_overlap_fraction(self, context_formulae, other, depth=0, verbose=False) -> float:
        #if other == syntax.reader.r('(if H (not Ma))') and is_atomic(self):
            #return -1000000
         
        attention_modals = set(map(lambda x: x.kernel, set(filter(lambda x: is_modal(x) and x.modal_type=="attention", context_formulae))))
        if  attention_modals and self in attention_modals:
            if verbose:
                indent = '\t'* depth
   #             print(Style.BRIGHT + f"{indent}Focussing on " + Style.RESET_ALL + Back.RED + Fore.WHITE + f"{self}" + Style.RESET_ALL)
    #            print(Style.RESET_ALL)

            return 100000

        x = self.get_sub_formulae()
        y = other.get_sub_formulae()
        d = max(len(x), len(y)) 
        if d == 0:
            return 0
        return len(set(x).intersection(y))/d
    
    def compute_similarity(self, other, depth=0, verbose=False) -> float:
        #if other == syntax.reader.r('(if H (not Ma))') and is_atomic(self):
            #return -1000000
         
        x = self.get_sub_expressions()
        y = other.get_sub_expressions()
        d = max(len(x), len(y)) 
        if d == 0:
            return 0
        return len(set(x).intersection(y))/d
    

    def __hash__(self):
        return hash(str(self.head) + str(self.args))

    def __ge__(self, other):
        return str(self) >= str(other)
    
def make_and(expressions):
    if not expressions:
        return expressions
    if len(expressions) ==1:
        return expressions[0]
    else:
        return Expression(Symbol("and"), expressions)
        
def make_or(expressions):
    if not expressions:
        return expressions
    if len(expressions) ==1:
        return expressions[0]
    else:
        return Expression(Symbol("or"), expressions)
    
def make_if(antecedent, consequent):
    return Expression(Symbol("if"), [antecedent, consequent])
    
def make_universal(variables, kernel):
    return r(f"(forall {variables} {kernel})")

def negated(expression):
    if is_not(expression):
        return expression.args[0]
    else:
        return Expression(Symbol("not"), [expression])

def is_equals(expression):
    head = expression.head
    return head == Symbol("=")


def is_not(expression):
    head = expression.head
    return head == Symbol("not") and len(expression.args) == 1


def is_and(expression):
    head = expression.head
    return head == Symbol("and") and len(expression.args) >= 2

def is_or(expression):
    head = expression.head
    return head == Symbol("or") and len(expression.args) >= 2

def is_if(expression):
    head = expression.head
    return head == Symbol("if") and len(expression.args) == 2

def is_iff(expression):
    head = expression.head
    return head == Symbol("iff") and len(expression.args) == 2

def is_forall(expression):
    head = expression.head
    return head == Symbol("forall") and len(expression.args) == 2

def is_exists(expression):
    head = expression.head
    return head == Symbol("exists") and len(expression.args) == 2

def is_quantifier(expression):
    return is_forall(expression) or is_exists(expression)

def is_modal(expression):
    return expression.is_modal()

def is_atomic(expression):
    non_atomic_preds = [
        is_not, is_and, is_or, is_if, is_iff, is_forall, is_exists, is_modal
    ]
    res = not any(
        [non_atomic_pred(expression) for non_atomic_pred in non_atomic_preds])
    return res


def get_bound_variables(expression):
    if is_quantifier(expression):
        
        variables_expression = expression.args[0] 

        bound_vars = [r(variables_expression.head.name)] + (variables_expression.args or [])
        return bound_vars
    else:
        return []