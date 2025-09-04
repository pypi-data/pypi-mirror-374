#OMSS imports
from omss import Ruletype, AttributeType, Rule
from .seed import random_rule

#general imports
from enum import Enum, auto

class ruleset (Enum):
    extremely_easy = auto () # all rules full constant, for now also combination of elements 
    very_easy = auto () #all rules constant and combination of elements with all full constant rules
    easy = auto () # one rule not constant, no arithmetic rules, no number rules except for line. Element combinations with all constant rules
    moderate = auto () # multiple rules combinations, arithmetic rules, single rules for numbers, angle progressions and combination of elements"
    advanced = auto () # arithmetic with non-constant aspects, triple rule combis, double rule combis for number progression and line elements, combination of elements with rules for each elemen
    very_advanced = auto () #kinda the sky is the limit, but then within limits (even crazier combinations are possible and some point i might add an extremely advanced set. but i think we are already close to maximising the difficulty)
    test = auto () #usefull for testing single rulesets              


def rules_generator (difficulty, seed_list):
    if difficulty == ruleset.extremely_easy:        
        selected_rules, seed_list = random_rule(seed_list, extremely_easy)
        return (selected_rules)
    
    if difficulty == ruleset.very_easy:        
        selected_rules, seed_list = random_rule(seed_list, very_easy)
        return (selected_rules)      
    
    if difficulty == ruleset.easy:        
        selected_rules, seed_list = random_rule(seed_list, easy)
        return (selected_rules)

    if difficulty == ruleset.moderate:        
        selected_rules, seed_list = random_rule(seed_list, moderate)
        return (selected_rules)
    
    if difficulty == ruleset.advanced:        
        selected_rules, seed_list = random_rule(seed_list,advanced)
        return (selected_rules)
    
    if difficulty == ruleset.very_advanced:        
        selected_rules, seed_list = random_rule(seed_list,very_advanced)
        return (selected_rules)

    if difficulty == ruleset.test:        
        selected_rules, seed_list = random_rule(seed_list,test)
        return (selected_rules)
    
# extremely easy problems, basically all full_constant 
EE_BS = {
    'BigShape': [       
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SHAPE),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.COLOR),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.NUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')]}

EE_LS = {
    'LittleShape': [       
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SHAPE),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.COLOR),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.LITTLESHAPENUMBER, value = 'four'),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')]}

EE_LI = {
    'Line': [       
        Rule(Ruletype.FULL_CONSTANT, AttributeType.LINETYPE),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.LINENUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.ANGLE)]}


EE_BS_LS = {
    'BigShape': [       
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SHAPE),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.COLOR),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.NUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')],
    
    'LittleShape': [       
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SHAPE),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.COLOR),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.LITTLESHAPENUMBER, value = 'four'),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')],       
        }


EE_BS_LI = {
    'BigShape': [       
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SHAPE),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.COLOR),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.NUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')],    
  
    'Line': [       
        Rule(Ruletype.FULL_CONSTANT, AttributeType.LINETYPE),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.LINENUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.ANGLE)],       
    
    }

# very easy problems, basically most rules constant 
VE_BS = {
    'BigShape': [       
        Rule(Ruletype.CONSTANT, AttributeType.SHAPE),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.CONSTANT, AttributeType.COLOR),
        Rule(Ruletype.CONSTANT, AttributeType.NUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')]}

VE_LS = {
    'LittleShape': [       
        Rule(Ruletype.CONSTANT, AttributeType.SHAPE),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.CONSTANT, AttributeType.COLOR),
        Rule(Ruletype.CONSTANT, AttributeType.LITTLESHAPENUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')]}

VE_LI = {
    'Line': [       
        Rule(Ruletype.CONSTANT, AttributeType.LINETYPE),
        Rule(Ruletype.CONSTANT, AttributeType.LINENUMBER),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE)]}

#easy problems 
### combinations of elements
E_BS_LS = {
    'BigShape': [       
        Rule(Ruletype.CONSTANT, AttributeType.SHAPE),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.CONSTANT, AttributeType.COLOR),
        Rule(Ruletype.CONSTANT, AttributeType.NUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')],
    
    'LittleShape': [       
        Rule(Ruletype.CONSTANT, AttributeType.SHAPE),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.CONSTANT, AttributeType.COLOR),
        Rule(Ruletype.CONSTANT, AttributeType.LITTLESHAPENUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')],       
        }


E_BS_LI = {
    'BigShape': [       
        Rule(Ruletype.CONSTANT, AttributeType.SHAPE),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.CONSTANT, AttributeType.COLOR),
        Rule(Ruletype.CONSTANT, AttributeType.NUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')],    
  
    'Line': [       
        Rule(Ruletype.CONSTANT, AttributeType.LINETYPE),
        Rule(Ruletype.CONSTANT, AttributeType.LINENUMBER),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE)],       
    
    }

### single elements but with a rule going ON
E_BS_DC = {
    'BigShape': [       
        Rule(Ruletype.CONSTANT, AttributeType.SHAPE),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.COLOR),
        Rule(Ruletype.CONSTANT, AttributeType.NUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')]}



E_BS_DS = {
    'BigShape': [       
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.SHAPE),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.CONSTANT, AttributeType.COLOR),
        Rule(Ruletype.CONSTANT, AttributeType.NUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')]}


E_BS_PS = {
    'BigShape': [       
        Rule(Ruletype.CONSTANT, AttributeType.SHAPE),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.CONSTANT, AttributeType.COLOR),
        Rule(Ruletype.CONSTANT, AttributeType.NUMBER),
        Rule(Ruletype.PROGRESSION, AttributeType.SIZE)]}


E_LS_PS = {
    'LittleShape': [       
        Rule(Ruletype.CONSTANT, AttributeType.SHAPE),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.CONSTANT, AttributeType.COLOR),
        Rule(Ruletype.CONSTANT, AttributeType.LITTLESHAPENUMBER),
        Rule(Ruletype.PROGRESSION, AttributeType.SIZE)]}


E_LS_DC = {
    'LittleShape': [       
        Rule(Ruletype.CONSTANT, AttributeType.SHAPE),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.COLOR),
        Rule(Ruletype.CONSTANT, AttributeType.LITTLESHAPENUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')]}

E_LI_PN = {
    'Line': [       
        Rule(Ruletype.CONSTANT, AttributeType.LINETYPE),
        Rule(Ruletype.PROGRESSION, AttributeType.LINENUMBER),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE)]}

E_LI_DT = {
    'Line': [       
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.LINETYPE),
        Rule(Ruletype.CONSTANT, AttributeType.LINENUMBER),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE)]}

#moderate problems
M_BS_PA = {
    'BigShape': [       
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SHAPE),
        Rule(Ruletype.PROGRESSION, AttributeType.ANGLE),
        Rule(Ruletype.CONSTANT, AttributeType.COLOR),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.NUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')]}

M_LI_PA= {
    'Line': [       
        Rule(Ruletype.CONSTANT, AttributeType.LINETYPE),
        Rule(Ruletype.CONSTANT, AttributeType.LINENUMBER),
        Rule(Ruletype.PROGRESSION, AttributeType.ANGLE)]}


M_BS_PS_DC = {
    'BigShape': [       
        Rule(Ruletype.CONSTANT, AttributeType.SHAPE),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.COLOR),
        Rule(Ruletype.CONSTANT, AttributeType.NUMBER),
        Rule(Ruletype.PROGRESSION, AttributeType.SIZE)]}

M_BS_DC_DC = {
    'BigShape': [       
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.SHAPE),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.COLOR),
        Rule(Ruletype.CONSTANT, AttributeType.NUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')]}

M_BS_PS= {
    'BigShape': [       
        Rule(Ruletype.PROGRESSION, AttributeType.SHAPE),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.CONSTANT, AttributeType.COLOR),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.NUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')]}


M_LS_PN = {
    'LittleShape': [       
        Rule(Ruletype.CONSTANT, AttributeType.SHAPE),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.CONSTANT, AttributeType.COLOR),
        Rule(Ruletype.PROGRESSION, AttributeType.LITTLESHAPENUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')]}
M_LS_DN = {
    'LittleShape': [       
        Rule(Ruletype.CONSTANT, AttributeType.SHAPE),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.CONSTANT, AttributeType.COLOR),
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.LITTLESHAPENUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')]}
M_LS_A = {
    'LittleShape': [       
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SHAPE),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.CONSTANT, AttributeType.COLOR),
        Rule(Ruletype.ARITHMETIC, AttributeType.LITTLESHAPENUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')]}


M_LI_A= {
    'Line': [       
        Rule(Ruletype.CONSTANT, AttributeType.LINETYPE),
        Rule(Ruletype.ARITHMETIC, AttributeType.LINENUMBER),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE)]}

M_LI_DT_DN= {
    'Line': [       
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.LINETYPE),
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.LINENUMBER),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE)]}

M_BSLS_A = {
    'BigShape': [       
        Rule(Ruletype.CONSTANT, AttributeType.SHAPE),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.CONSTANT, AttributeType.COLOR),
        Rule(Ruletype.ARITHMETIC, AttributeType.NUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')],
    
    'LittleShape': [       
        Rule(Ruletype.CONSTANT, AttributeType.SHAPE),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.CONSTANT, AttributeType.COLOR),
        Rule(Ruletype.ARITHMETIC, AttributeType.LITTLESHAPENUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')]}

M_BSLI_A = {
    'BigShape': [       
        Rule(Ruletype.CONSTANT, AttributeType.SHAPE),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.CONSTANT, AttributeType.COLOR),
        Rule(Ruletype.ARITHMETIC, AttributeType.NUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')],
    
    'Line': [       
        Rule(Ruletype.CONSTANT, AttributeType.LINETYPE),
        Rule(Ruletype.ARITHMETIC, AttributeType.LINENUMBER),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE)]}



M_BS_DS_LS = {
    'BigShape': [       
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.SHAPE),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.CONSTANT, AttributeType.COLOR),
        Rule(Ruletype.CONSTANT, AttributeType.NUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')],
    
    'LittleShape': [       
        Rule(Ruletype.CONSTANT, AttributeType.SHAPE),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.CONSTANT, AttributeType.COLOR),
        Rule(Ruletype.CONSTANT, AttributeType.LITTLESHAPENUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')]}

M_BS_DC_LS = {
    'BigShape': [       
        Rule(Ruletype.CONSTANT, AttributeType.SHAPE),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.COLOR),
        Rule(Ruletype.CONSTANT, AttributeType.NUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')],
    
    'LittleShape': [       
        Rule(Ruletype.CONSTANT, AttributeType.SHAPE),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.CONSTANT, AttributeType.COLOR),
        Rule(Ruletype.CONSTANT, AttributeType.LITTLESHAPENUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')]}

M_BS_LS_DC = {
    'BigShape': [       
        Rule(Ruletype.CONSTANT, AttributeType.SHAPE),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.CONSTANT, AttributeType.COLOR),
        Rule(Ruletype.CONSTANT, AttributeType.NUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')],
    
    'LittleShape': [       
        Rule(Ruletype.CONSTANT, AttributeType.SHAPE),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.COLOR),
        Rule(Ruletype.CONSTANT, AttributeType.LITTLESHAPENUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')]}

M_BS_DS_LI = {
    'BigShape': [       
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.SHAPE),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.CONSTANT, AttributeType.COLOR),
        Rule(Ruletype.CONSTANT, AttributeType.NUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')],
    
    'Line': [       
        Rule(Ruletype.CONSTANT, AttributeType.LINETYPE),
        Rule(Ruletype.CONSTANT, AttributeType.LINENUMBER),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE)]}

M_BS_LI_DT = {
    'BigShape': [       
        Rule(Ruletype.CONSTANT, AttributeType.SHAPE),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.CONSTANT, AttributeType.COLOR),
        Rule(Ruletype.CONSTANT, AttributeType.NUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')],
    
    'Line': [       
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.LINETYPE),
        Rule(Ruletype.CONSTANT, AttributeType.LINENUMBER),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE)]}


#advanced problems


#maybe these first ones are a bit too difficult for advanced, it depends
A_BSLI_A_DT = {
    'BigShape': [       
        Rule(Ruletype.CONSTANT, AttributeType.SHAPE),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.CONSTANT, AttributeType.COLOR),
        Rule(Ruletype.ARITHMETIC, AttributeType.NUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')],
    
    'Line': [       
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.LINETYPE),
        Rule(Ruletype.ARITHMETIC, AttributeType.LINENUMBER),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE)]}



A_BSLS_A_DS = {
    'BigShape': [       
        Rule(Ruletype.CONSTANT, AttributeType.SHAPE),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.CONSTANT, AttributeType.COLOR),
        Rule(Ruletype.ARITHMETIC, AttributeType.NUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')],
    
    'LittleShape': [       
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.SHAPE),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.CONSTANT, AttributeType.COLOR),
        Rule(Ruletype.ARITHMETIC, AttributeType.LITTLESHAPENUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')]}

A_BSLS_A_DC = {
    'BigShape': [       
        Rule(Ruletype.CONSTANT, AttributeType.SHAPE),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.CONSTANT, AttributeType.COLOR),
        Rule(Ruletype.ARITHMETIC, AttributeType.NUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')],
    
    'LittleShape': [       
        Rule(Ruletype.CONSTANT, AttributeType.SHAPE),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.COLOR),
        Rule(Ruletype.ARITHMETIC, AttributeType.LITTLESHAPENUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')]}



M_BS_PS_DC2 = {
    'BigShape': [       
        Rule(Ruletype.PROGRESSION, AttributeType.SHAPE),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.COLOR),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.NUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')]}



A_BS_PS_DS= {
    'BigShape': [       
        Rule(Ruletype.PROGRESSION, AttributeType.SHAPE),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.CONSTANT, AttributeType.COLOR),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.NUMBER),
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.SIZE)]}

A_BS_PA_DC= {
    'BigShape': [       
        Rule(Ruletype.CONSTANT, AttributeType.SHAPE),
        Rule(Ruletype.PROGRESSION, AttributeType.ANGLE),
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.COLOR),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.NUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')]}





A_LS_A_DS = {
    'LittleShape': [       
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.SHAPE),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.CONSTANT, AttributeType.COLOR),
        Rule(Ruletype.ARITHMETIC, AttributeType.LITTLESHAPENUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')]}

A_LS_A_DC = {
    'LittleShape': [       
        Rule(Ruletype.CONSTANT, AttributeType.SHAPE),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.COLOR),
        Rule(Ruletype.ARITHMETIC, AttributeType.LITTLESHAPENUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')]}

A_LS_PN_DC = {
    'LittleShape': [       
        Rule(Ruletype.CONSTANT, AttributeType.SHAPE),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.COLOR),
        Rule(Ruletype.PROGRESSION, AttributeType.LITTLESHAPENUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')]}

A_LS_PN_DS = {
    'LittleShape': [       
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.SHAPE),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.CONSTANT, AttributeType.COLOR),
        Rule(Ruletype.PROGRESSION, AttributeType.LITTLESHAPENUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')]}

A_LS_DN_DS = {
    'LittleShape': [       
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.SHAPE),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.CONSTANT, AttributeType.COLOR),
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.LITTLESHAPENUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')]}



A_LI_A_DT= {
    'Line': [       
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.LINETYPE),
        Rule(Ruletype.ARITHMETIC, AttributeType.LINENUMBER),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE)]}

A_LI_A_PA= {
    'Line': [       
        Rule(Ruletype.CONSTANT, AttributeType.LINETYPE),
        Rule(Ruletype.ARITHMETIC, AttributeType.LINENUMBER),
        Rule(Ruletype.PROGRESSION, AttributeType.ANGLE)]}

A_LI_PN_PA= {
    'Line': [       
        Rule(Ruletype.CONSTANT, AttributeType.LINETYPE),
        Rule(Ruletype.PROGRESSION, AttributeType.LINENUMBER),
        Rule(Ruletype.PROGRESSION, AttributeType.ANGLE)]}

A_LI_DN_PA= {
    'Line': [       
        Rule(Ruletype.CONSTANT, AttributeType.LINETYPE),
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.LINENUMBER),
        Rule(Ruletype.PROGRESSION, AttributeType.ANGLE)]}

A_BS_DS_LS_DC = {
    'BigShape': [       
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.SHAPE),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.CONSTANT, AttributeType.COLOR),
        Rule(Ruletype.CONSTANT, AttributeType.NUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')],
    
    'LittleShape': [       
        Rule(Ruletype.CONSTANT, AttributeType.SHAPE),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.COLOR),
        Rule(Ruletype.CONSTANT, AttributeType.LITTLESHAPENUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')]}


A_BS_DC_LS_DC = {
    'BigShape': [       
        Rule(Ruletype.CONSTANT, AttributeType.SHAPE),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.COLOR),
        Rule(Ruletype.CONSTANT, AttributeType.NUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')],
    
    'LittleShape': [       
        Rule(Ruletype.CONSTANT, AttributeType.SHAPE),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.COLOR),
        Rule(Ruletype.CONSTANT, AttributeType.LITTLESHAPENUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')]}

A_BS_DS_LI_DT = {
    'BigShape': [       
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.SHAPE),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.CONSTANT, AttributeType.COLOR),
        Rule(Ruletype.CONSTANT, AttributeType.NUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')],
    
    'Line': [       
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.LINETYPE),
        Rule(Ruletype.CONSTANT, AttributeType.LINENUMBER),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE)]}

A_BS_DS_LI_PA = {
    'BigShape': [       
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.SHAPE),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.CONSTANT, AttributeType.COLOR),
        Rule(Ruletype.CONSTANT, AttributeType.NUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')],
    
    'Line': [       
        Rule(Ruletype.CONSTANT, AttributeType.LINETYPE),
        Rule(Ruletype.CONSTANT, AttributeType.LINENUMBER),
        Rule(Ruletype.PROGRESSION, AttributeType.ANGLE)]}


#very advanced
VA_LS_DS_DC= {
    'LittleShape': [       
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.SHAPE),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.CONSTANT, AttributeType.COLOR),
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.LITTLESHAPENUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')]}

VA_LI_DT_DN_PA= {
    'Line': [       
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.LINETYPE),
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.LINENUMBER),
        Rule(Ruletype.PROGRESSION, AttributeType.ANGLE)]}



VA_LS_DC_LI_A = {
    'LittleShape': [       
        Rule(Ruletype.CONSTANT, AttributeType.SHAPE),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.COLOR),
        Rule(Ruletype.ARITHMETIC, AttributeType.LITTLESHAPENUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')],
    
    'Line': [       
        Rule(Ruletype.CONSTANT, AttributeType.LINETYPE),
        Rule(Ruletype.ARITHMETIC, AttributeType.LINENUMBER),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE)]}



VA_LS_LI_A_DT = {
    'LittleShape': [       
        Rule(Ruletype.CONSTANT, AttributeType.SHAPE),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.CONSTANT, AttributeType.COLOR),
        Rule(Ruletype.ARITHMETIC, AttributeType.LITTLESHAPENUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')],
    
    'Line': [       
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.LINETYPE),
        Rule(Ruletype.ARITHMETIC, AttributeType.LINENUMBER),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE)]}



VA_LS_DS_LI_A = {
    'LittleShape': [       
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.SHAPE),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.CONSTANT, AttributeType.COLOR),
        Rule(Ruletype.ARITHMETIC, AttributeType.LITTLESHAPENUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')],
    
    'Line': [       
        Rule(Ruletype.CONSTANT, AttributeType.LINETYPE),
        Rule(Ruletype.ARITHMETIC, AttributeType.LINENUMBER),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE)]}


VA_LS_PN_LI_A = {
    'LittleShape': [       
        Rule(Ruletype.CONSTANT, AttributeType.SHAPE),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.CONSTANT, AttributeType.COLOR),
        Rule(Ruletype.PROGRESSION, AttributeType.LITTLESHAPENUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')],
    
    'Line': [       
        Rule(Ruletype.CONSTANT, AttributeType.LINETYPE),
        Rule(Ruletype.ARITHMETIC, AttributeType.LINENUMBER),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE)]}

VA_LS_PN_LI_PN = {
    'LittleShape': [       
        Rule(Ruletype.CONSTANT, AttributeType.SHAPE),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.CONSTANT, AttributeType.COLOR),
        Rule(Ruletype.PROGRESSION, AttributeType.LITTLESHAPENUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')],
    
    'Line': [       
        Rule(Ruletype.CONSTANT, AttributeType.LINETYPE),
        Rule(Ruletype.PROGRESSION, AttributeType.LINENUMBER),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE)]}

VA_LS_DS_LI_DT_DN = {
    'LittleShape': [       
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.SHAPE),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.CONSTANT, AttributeType.COLOR),
        Rule(Ruletype.CONSTANT, AttributeType.LITTLESHAPENUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')],
    
    'Line': [       
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.LINETYPE),
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.LINENUMBER),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE)]}

VA_LS_A_LI_DT_DN = {
    'LittleShape': [       
        Rule(Ruletype.CONSTANT, AttributeType.SHAPE),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.CONSTANT, AttributeType.COLOR),
        Rule(Ruletype.ARITHMETIC, AttributeType.LITTLESHAPENUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')],
    
    'Line': [       
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.LINETYPE),
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.LINENUMBER),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE)]}



VA_BS_PS_LS_DS_DC= {
    'BigShape': [       
        Rule(Ruletype.PROGRESSION, AttributeType.SHAPE),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.CONSTANT, AttributeType.COLOR),
        Rule(Ruletype.CONSTANT, AttributeType.NUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')],
    
    'LittleShape': [       
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.SHAPE),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.COLOR),
        Rule(Ruletype.CONSTANT, AttributeType.LITTLESHAPENUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')]}

VA_BS_A_LS_DN= {
    'BigShape': [       
        Rule(Ruletype.CONSTANT, AttributeType.SHAPE),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.CONSTANT, AttributeType.COLOR),
        Rule(Ruletype.ARITHMETIC, AttributeType.NUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')],
    
    'LittleShape': [       
        Rule(Ruletype.CONSTANT, AttributeType.SHAPE),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.CONSTANT, AttributeType.COLOR),
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.LITTLESHAPENUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')]}

VA_BS_A_LS_DS_DC = {
    'BigShape': [       
        Rule(Ruletype.CONSTANT, AttributeType.SHAPE),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.CONSTANT, AttributeType.COLOR),
        Rule(Ruletype.ARITHMETIC, AttributeType.NUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')],
    
    'LittleShape': [       
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.SHAPE),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.COLOR),
        Rule(Ruletype.ARITHMETIC, AttributeType.LITTLESHAPENUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')]}

VA_BS_PS_DC_LS_DS_A = {
    'BigShape': [       
        Rule(Ruletype.PROGRESSION, AttributeType.SHAPE),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.COLOR),
        Rule(Ruletype.CONSTANT, AttributeType.NUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')],
    
    'LittleShape': [       
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.SHAPE),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.CONSTANT, AttributeType.COLOR),
        Rule(Ruletype.ARITHMETIC, AttributeType.LITTLESHAPENUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')]}

VA_BS_DCS_LS_DSC= {
    'BigShape': [       
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.SHAPE),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.COLOR),
        Rule(Ruletype.CONSTANT, AttributeType.NUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')],
    
    'LittleShape': [       
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.SHAPE),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.COLOR),
        Rule(Ruletype.CONSTANT, AttributeType.LITTLESHAPENUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')]}

VA_BS_DCS_LS_DSN= {
    'BigShape': [       
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.SHAPE),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.COLOR),
        Rule(Ruletype.CONSTANT, AttributeType.NUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')],
    
    'LittleShape': [       
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.SHAPE),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.CONSTANT, AttributeType.COLOR),
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.LITTLESHAPENUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')]}

VA_BS_DA_DC = {
    'BigShape': [       
        Rule(Ruletype.CONSTANT, AttributeType.SHAPE),
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.ANGLE),
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.COLOR),
        Rule(Ruletype.CONSTANT, AttributeType.NUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')]}

VA_BS_PA_PS_DC = {
    'BigShape': [       
        Rule(Ruletype.PROGRESSION, AttributeType.SHAPE),
        Rule(Ruletype.PROGRESSION, AttributeType.ANGLE),
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.COLOR),
        Rule(Ruletype.CONSTANT, AttributeType.NUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')]}

VA_LS_PA_A = {
    'LittleShape': [       
        Rule(Ruletype.CONSTANT, AttributeType.SHAPE),
        Rule(Ruletype.PROGRESSION, AttributeType.ANGLE),
        Rule(Ruletype.CONSTANT, AttributeType.COLOR),
        Rule(Ruletype.ARITHMETIC, AttributeType.LITTLESHAPENUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')]}

VA_LS_DCNS = {
    'LittleShape': [       
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.SHAPE),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.COLOR),
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.LITTLESHAPENUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')]}

VA_LS_DS_PS_A = {
    'LittleShape': [       
        Rule(Ruletype.PROGRESSION, AttributeType.SHAPE),
        Rule(Ruletype.CONSTANT, AttributeType.ANGLE),
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.COLOR),
        Rule(Ruletype.ARITHMETIC, AttributeType.LITTLESHAPENUMBER),
        Rule(Ruletype.FULL_CONSTANT, AttributeType.SIZE, value = 'medium')]}

   
VA_LI_DT_PA_A= {
    'Line': [       
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.LINETYPE),
        Rule(Ruletype.ARITHMETIC, AttributeType.LINENUMBER),
        Rule(Ruletype.PROGRESSION, AttributeType.ANGLE)]}

VA_LI_PA_A= {
    'Line': [       
        Rule(Ruletype.CONSTANT, AttributeType.LINETYPE),
        Rule(Ruletype.ARITHMETIC, AttributeType.LINENUMBER),
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.ANGLE)]}
 
VA_LI_PA_PN= {
    'Line': [       
        Rule(Ruletype.CONSTANT, AttributeType.LINETYPE),
        Rule(Ruletype.PROGRESSION, AttributeType.LINENUMBER),
        Rule(Ruletype.DISTRIBUTE_THREE, AttributeType.ANGLE)]}

test = [VA_LS_LI_A_DT]

"extremely easy: all rules full constant, no combination of elements"
extremely_easy = [EE_BS, EE_LI, EE_LS] #some things doubled to improve there chances of occuring

"very easy: all rules constant, also combination of elements with full constant rules "
very_easy = [VE_BS, VE_LI, VE_LS,VE_BS, VE_LI, VE_LS, EE_BS_LS, EE_BS_LI] #some things doubled to improve there chances of occuring

"easy: one rule not constant, no arithmetic rules, no number rules except for line. Element combinations with all constant rules" 
easy = [E_BS_DC, E_BS_DS, E_BS_DC, E_BS_DS,  E_BS_PS, E_LS_PS, E_LS_DC,E_LI_PN, E_LI_DT, E_LS_DC,E_BS_LS, E_BS_LI] 
# all things doubled except for size rules, combinations and lines, to decrease the changes of the size rule and line element (was a bit too often)


"moderate: multiple rules combinations,arithmetic rules, single rules for numbers, angle progressions and combination of elements"
moderate = [M_BS_PA, M_LI_PA, M_BS_PS_DC, M_BS_DC_DC, M_LS_PN, M_LS_DN, M_LS_A, 
            M_LI_A,  M_BSLS_A, M_BSLI_A, M_BS_PS,M_BS_DS_LS, M_BS_DC_LS, M_BS_LS_DC,M_BS_DS_LI,M_BS_LI_DT]


"advanced: arithmetic with non-constant aspects, triple rule combis, double rule combis for number progression and line elements, combination of elements with rules for each element"
advanced = [A_BSLI_A_DT, A_BSLS_A_DS, A_BSLS_A_DC, A_BS_PS_DS, A_BS_PA_DC,A_LS_A_DS,A_LS_A_DC,A_LS_PN_DC,
            A_LS_PN_DS, M_LI_DT_DN, A_LS_DN_DS,A_LI_A_DT, A_LI_PN_PA ,A_LI_DN_PA, A_BS_DS_LS_DC,A_BS_DC_LS_DC,A_BS_DS_LI_DT,M_BS_PS_DC2 ]

"very advanced: a lot is going one, but still somewhat within limits. they could be even crazier but i think this is already close to maximum difficulty"
very_advanced = [A_LI_A_PA, VA_LS_DC_LI_A,VA_LS_LI_A_DT,VA_LS_DS_DC,VA_LI_DT_DN_PA, VA_LS_DS_LI_A,VA_LS_PN_LI_A,VA_LS_PN_LI_PN, VA_LS_DS_LI_DT_DN,
                 VA_LS_A_LI_DT_DN,VA_BS_PS_LS_DS_DC,VA_BS_A_LS_DN, VA_BS_A_LS_DS_DC,VA_BS_PS_DC_LS_DS_A,VA_BS_DCS_LS_DSC,
                 VA_BS_DCS_LS_DSN,VA_BS_DA_DC, VA_BS_PA_PS_DC,VA_LS_PA_A,VA_LS_DCNS,VA_LI_DT_PA_A, VA_LI_PA_A,VA_LI_PA_PN ]


