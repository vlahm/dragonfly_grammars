# Dragonfly module for controlling vim on Linux modelessly. All verbal commands
# start and end in command mode, making it effective to combine voice and
# keyboard.
#

LEADER = 'comma'

import aenea.config
import aenea.misc
import aenea.vocabulary

from aenea import (
    #MappingRule,
    #Grammar,
    Key,
    NoAction,
    Text
    )

from aenea.proxy_contexts import ProxyAppContext

from dragonfly import (
    Alternative,
    AppContext,
    CompoundRule,
    Dictation,
    Grammar,
    MappingRule,
    Repetition,
    RuleRef,
    Choice,
    IntegerRef
    )

vim_context = aenea.wrappers.AeneaContext(
    ProxyAppContext(match='regex', title='Rstudio'),
    AppContext(title='Rstudio')
    )

command_t_context = aenea.wrappers.AeneaContext(
    ProxyAppContext(match='regex', title='^GoToFile.*$'),
    AppContext(title='GoToFile')
    ) & vim_context

fugitive_index_context = aenea.wrappers.AeneaContext(
    ProxyAppContext(match='regex', title='^index.*\.git.*$'),
    AppContext(title='index') & AppContext('.git')
    ) & vim_context

#grammar = Grammar('vim')
grammar = Grammar('vim', context=vim_context)

from dragonfly import DictListRef

VIM_TAGS = ['vim.insertions.code', 'vim.insertions']
aenea.vocabulary.inhibit_global_dynamic_vocabulary('vim', VIM_TAGS, vim_context)

#class TestRule(MappingRule):
#    mapping = {
#          'alpha': Text('a'),
#          'donkey': Text('youre a donkey'),
#        }
#
#grammar.add_rule(TestRule())


#grammar.add_rule(TestRule())


# TODO: this can NOT be the right way to do this...
class NumericDelegateRule(CompoundRule):
    def value(self, node):
        delegates = node.children[0].children[0].children
        value = delegates[-1].value()
        if delegates[0].value() is not None:
            return Text('%s' % delegates[0].value()) + value
        else:
            return value


class _DigitalIntegerFetcher(object):
    def __init__(self):
        self.cached = {}

    def __getitem__(self, length):
        if length not in self.cached:
            self.cached[length] = aenea.misc.DigitalInteger('count', 1, length)
        return self.cached[length]
ruleDigitalInteger = _DigitalIntegerFetcher()


class LetterMapping(MappingRule):
    mapping = aenea.misc.LETTERS
ruleLetterMapping = RuleRef(LetterMapping(), name='LetterMapping')


def execute_insertion_buffer(insertion_buffer):
    if not insertion_buffer:
        return

    if insertion_buffer[0][0] is not None:
        insertion_buffer[0][0].execute()
    else:
        pass
        #Key('a').execute()

    for insertion in insertion_buffer:
        insertion[1].execute()

    #Key('escape:2').execute()

# ****************************************************************************
# IDENTIFIERS
# ****************************************************************************


class InsertModeEntry(MappingRule):
    mapping = {
        'inns': Key('i'),
        'syn': Key('a'),
        'phyllo': Key('escape, escape, o'),
        'phylum': Key('escape, escape, O'),
        }
ruleInsertModeEntry = RuleRef(InsertModeEntry(), name='InsertModeEntry')


def format_snakeword(text):
    formatted = text[0][0].upper()
    formatted += text[0][1:]
    formatted += ('_' if len(text) > 1 else '')
    formatted += format_eelword(text[1:])
    return formatted


def format_eelword(text):
    return '_'.join(text)

def format_acronym(text):
    return ''.join([word.upper() for word in text])


def format_camel(text):
    return text[0] + ''.join([word[0].upper() + word[1:] for word in text[1:]])


def format_proper(text):
    return ''.join(word.capitalize() for word in text)


def format_relpath(text):
    return '/'.join(text)


def format_abspath(text):
    return '/' + format_relpath(text)


def format_scoperesolve(text):
    return '::'.join(text)


def format_jumble(text):
    return ''.join(text)


def format_dotword(text):
    return '.'.join(text)


def format_dashword(text):
    return '-'.join(text)


def format_natword(text):
    return ' '.join(text)


def format_lowercase(text):
    return ' '.join([word.lower() for word in text])
def format_uppercase(text):
    return ' '.join([word.upper() for word in text])
def format_stringsequence(text):
    return "'" + "', '".join(text) + "'"
def format_superstringsequence(text):
    return '"' + '", "'.join(text) + '"'
def format_commasequence(text):
    return ', '.join(text)


def format_broodingnarrative(text):
    return ''


def format_sentence(text):
    return ' '.join([text[0].capitalize()] + text[1:])


class IdentifierInsertion(CompoundRule):
    spec = ('[upper | natural] ( proper | camel | rel-path | abs-path | eelword | sentence | uppercase | lowercase | '
            'scope-resolve | jumble | dotword | dashword | natword | snakeword | brooding-narrative | '
            'string-sequence | superstring-sequence | comma-sequence | acronym) [<dictation>]')
    extras = [Dictation(name='dictation')]

    def value(self, node):
        words = node.words()

        uppercase = words[0] == 'upper'
        lowercase = words[0] != 'natural'

        if lowercase:
            words = [word.lower() for word in words]
        if uppercase:
            words = [word.upper() for word in words]

        words = [word.split('\\', 1)[0].replace('-', '') for word in words]
        if words[0].lower() in ('upper', 'natural'):
            del words[0]

        function = globals()['format_%s' % words[0].lower()]
        formatted = function(words[1:])

        return Text(formatted)
ruleIdentifierInsertion = RuleRef(
    IdentifierInsertion(),
    name='IdentifierInsertion'
    )


class LiteralIdentifierInsertion(CompoundRule):
    spec = '[<InsertModeEntry>] literal <IdentifierInsertion>'
    extras = [ruleIdentifierInsertion, ruleInsertModeEntry]

    def value(self, node):
        children = node.children[0].children[0].children
        return [('i', (children[0].value(), children[2].value()))]
ruleLiteralIdentifierInsertion = RuleRef(
    LiteralIdentifierInsertion(),
    name='LiteralIdentifierInsertion'
    )


# ****************************************************************************
# INSERTIONS
# ****************************************************************************

class KeyInsertion(MappingRule):
    mapping = {
        '<text>':               Text('%(text)s'), #catch-all for text
        'ace [<count>]':        Key('space:%(count)d'),
        'tab [<count>]':        Key('tab:%(count)d'),
        'slap [<count>]':       Key('enter:%(count)d'),
        'chuck [<count>]':      Key('del:%(count)d'),
        'scratch [<count>]':    Key('backspace:%(count)d'),
        'nix [<count>]':        Key('x:%(count)d'),
        'scroll up [<count>]':        Key('c-y:%(count)d'),
        'scroll down [<count>]':        Key('c-e:%(count)d'),
        'ack':                  Key('escape'),
        'bubble':               Key('lparen, rparen, left'),
        'box':                  Key('lbracket, rbracket, left'),
        'mandolin':             Key('lbrace, rbrace, left'),
        'substring':            Key('squote, squote, left'),
        'superstring':          Key('dquote/25:2, left'),
        'sundew [<count>]':     Key('c-z/25:%(count)d'),
        'sundry [<count>]':     Key('cs-z:%(count)d'),
        'sprint':               Key('ctrl:down'),
        'halt':                 Key('ctrl:up'),
        'highlight':            Key('shift:down'),
        'stoplight':            Key('shift:up'),
        'highlighter':          Key('ctrl:down, shift:down'),
        'stoplighter':          Key('ctrl:up, shift:up'),
        'copy':                 Key('c-c'),
        'cutout':               Key('c-x'),
        'pastry':               Key('c-v'),
        'savory':               Key('c-s'),
        'close tab':            Key('c-w'),
        'deloris':              Key('c-d'),
        'tasman right [<count>]': Key('c-tab/25:%(count)d'),
        'tasman left [<count>]': Key('cs-tab/25:%(count)d'),
        'console pane':         Key('c-2'),
        'script pane':          Key('c-1'),
        'console clear':        Key('c-l'),
        'shortcuts':            Key('as-k'),
        'restarter':            Key('cs-f10'),
        'help file':            Key('f1'),
        'function def':            Key('f2'),
        'collapse all':         Key('a-o'),
        'expand all':           Key('as-o'),
        'collapse one':         Key('a-l'),
        'expand one':           Key('as-l'),
        'source from beginning': Key('ca-b'),
        'source to end':        Key('ca-e'),
        'comment lines':        Key('cs-c'),
#"[<n>] up": Key("up:%(n)d"),
#       "[<n>] down": Key("down:%(n)d"),
#       "[<n>] left": Key("left:%(n)d"),
#       "[<n>] right": Key("right:%(n)d"),
        'up [<count>]':         Key('up:%(count)d'),
        'down [<count>]':       Key('down:%(count)d'),
        'left [<count>]':       Key('left:%(count)d'),
        'right [<count>]':      Key('right:%(count)d'),
        'goose <count>':      Key('escape') + Text('%(count)d') + Text('G'),
        'pipet':                Key('space, percent, rangle, percent, enter'),
        "run on [<count>]":     Key("c-enter:%(count)d"),
        "run stay":             Key("a-enter"),
        "last line":            Key("c-end"),
        "first line":           Key("c-home"),
        "commando":             Key("cs-c"),
        }
    extras = [
        Dictation("text"),
        ruleDigitalInteger[3]
        ]
    defaults = {'count': 1}
ruleKeyInsertion = RuleRef(KeyInsertion(), name='KeyInsertion')


class SpellingInsertion(MappingRule):
    mapping = dict(('dig ' + key, val) for (key, val) in aenea.misc.DIGITS.iteritems())
    mapping.update(aenea.misc.LETTERS)

    def value(self, node):
        return Text(MappingRule.value(self, node))
ruleSpellingInsertion = RuleRef(SpellingInsertion(), name='SpellingInsertion')


class ArithmeticInsertion(MappingRule):
    mapping = {
        'assign':           Text(' = '),
        'assigner':         Text(' <- '),
        'equals':           Text('='),
        'compare eek':      Text(' == '),
        'compare not eek':  Text(' != '),
        'compare greater':  Text(' > '),
        'compare less':     Text(' < '),
        'compare geck':     Text(' >= '),
        'compare lack':     Text(' <= '),
        'bit ore':          Text(' | '),
        'bit and':          Text(' & '),
        'bit ex or':        Text(' ^ '),
        'powder':        Text('^'),
        'operate multiply':            Text(' * '),
        'operate divide':          Text(' / '),
        'operate plus':             Text(' + '),
        'operate minus':            Text(' - '),
        'plus equal':       Text(' += '),
        'minus equal':      Text(' -= '),
        'times equal':      Text(' *= '),
        'divided equal':    Text(' /= '),
        'mod equal':        Text(' %%= '),
        'zero':             Text('0'),
        'num one':              Text('1'),
       'num two':              Text('2'),
       'num three':             Text('3'),
       'num four':            Text('4'),
       'num five':             Text('5'),
       'num six':              Text('6'),
       'num seven':            Text('7'),
       'num eight':            Text('8'),
       'num nine':            Text('9'),
        'nine':             Text('9'),
        'ten':              Text('10'),
        'eleven':           Text('11'),
        'twelve':           Text('12'),
        'thirteen':         Text('13'),
        'fourteen':         Text('14'),
        'fifteen':          Text('15'),
        'sixteen':          Text('16'),
        'seventeen':        Text('17'),
        'eighteen':         Text('18'),
        'nineteen':         Text('19'),
        'twenty':           Text('20'),
        'backslash':        Text('\\'),
        'commerce':         Text(', '),
        'commadore':        Key('right, comma, space'),
        'onward':        Key('right, space'),
        'baubles':        Key('space, percent, percent, left'),
        'commune':          Key('comma, enter'),
        'colony':           Text(': '),
        'colonial':         Key('comma, enter'),
        'vector':           Key('c, lparen, rparen, left'),
        'comment':          Text('# '),
        'quadcommendo':     Key('hash, hash, hash, hash, enter, enter'),
        'function start':   Key('space, equals, space, f, u, n, c, t, i, o, n, lparen, rparen, lbrace, left:2'),
        'function next':    Key('escape, escape, o, enter, enter, r, e, t, u, r, n, lparen, rparen, enter, rbrace, up, up, up, end'),
        'for loop start':   Key('f, o, r, lparen, i, space, i, n, space, rparen, lbrace, left:2'),
        'for loop next':    Key('escape, escape, o, enter, rbrace, up, end'),
        'bang':             Text('! '),
        'banger':           Text('!!'),
       'chap alpha':            Text('A'),
       'chap bravo':		Text('B'),
       'chap charlie':            Text('C'),
       'chap delta':            Text('D'),
       'chap echo':            Text('E'),
       'chap foxtrot':            Text('F'),
       'chap golf':            Text('G'),
       'chap hotel':            Text('H'),
       'chap indigo':            Text('I'),
       'chap juliet':            Text('J'),
       'chap kilo':            Text('K'),
       'chap lima':            Text('L'),
       'chap mango':            Text('M'),
       'chap november':            Text('N'),
       'chap oscar':            Text('O'),
       'chap poppa':            Text('P'),
       'chap quiche':            Text('Q'),
       'chap romeo':            Text('R'),
       'chap sierra':            Text('S'),
       'chap tango':            Text('T'),
       'chap uniform':            Text('U'),
       'chap victor':            Text('V'),
       'chap whiskey':            Text('W'),
       'chap x-ray':            Text('X'),
       'chap yankee':            Text('Y'),
       'chap zulu':            Text('Z'),

       'phil':			Text('fill'),
       'Ro':			Text('row'),
       'daytime':			Text('datetime'),
	'tibble':	Text('tibble'),
	'right hand side':	Text('right'),
        }
ruleArithmeticInsertion = RuleRef(
    ArithmeticInsertion(),
    name='ArithmeticInsertion'
    )


primitive_insertions = [
    ruleKeyInsertion,
    ruleIdentifierInsertion,
    DictListRef(
        'dynamic vim.insertions.code',
        aenea.vocabulary.register_dynamic_vocabulary('vim.insertions.code')
        ),
    DictListRef(
        'dynamic vim.insertions',
        aenea.vocabulary.register_dynamic_vocabulary('vim.insertions')
        ),
    ruleArithmeticInsertion,
    ruleSpellingInsertion,
    ]


static_code_insertions = aenea.vocabulary.get_static_vocabulary('vim.insertions.code')
static_insertions = aenea.vocabulary.get_static_vocabulary('vim.insertions')

if static_code_insertions:
    primitive_insertions.append(
        RuleRef(
            MappingRule(
                'static vim.insertions,code mapping',
                mapping=aenea.vocabulary.get_static_vocabulary('vim.insertions.code')
                ),
            'static vim.insertions.code'
            )
        )

if static_insertions:
    primitive_insertions.append(
        RuleRef(
            MappingRule(
                'static vim.insertions mapping',
                mapping=aenea.vocabulary.get_static_vocabulary('vim.insertions')
                ),
            'static vim.insertions'
            )
        )


class PrimitiveInsertion(CompoundRule):
    spec = '<insertion>'
    extras = [Alternative(primitive_insertions, name='insertion')]

    def value(self, node):
        children = node.children[0].children[0].children
        return children[0].value()
rulePrimitiveInsertion = RuleRef(
    PrimitiveInsertion(),
    name='PrimitiveInsertion'
    )


class PrimitiveInsertionRepetition(CompoundRule):
    spec = '<PrimitiveInsertion> [ parrot <count> ]'
    extras = [rulePrimitiveInsertion, ruleDigitalInteger[3]]

    def value(self, node):
        children = node.children[0].children[0].children
        holder = children[1].value()[1] if children[1].value() else 1
        value = children[0].value() * holder
        return value
rulePrimitiveInsertionRepetition = RuleRef(
    PrimitiveInsertionRepetition(),
    name='PrimitiveInsertionRepetition'
    )


class Insertion(CompoundRule):
    spec = '[<InsertModeEntry>] <PrimitiveInsertionRepetition>'
    extras = [rulePrimitiveInsertionRepetition, ruleInsertModeEntry]

    def value(self, node):
        children = node.children[0].children[0].children
        return [('i', (children[0].value(), children[1].value()))]
ruleInsertion = RuleRef(Insertion(), name='Insertion')


# ****************************************************************************
# MOTIONS
# ****************************************************************************


class PrimitiveMotion(MappingRule):
    mapping = {
        'upward': Text('k'),
        'downward': Text('j'),
        'leftward': Text('h'),
        'rightward': Text('l'),

        'lope': Text('b'),
        'yope': Text('w'),
        'elope': Text('ge'),
        'iyope': Text('e'),

        'lopert': Text('B'),
        'yopert': Text('W'),
        'elopert': Text('gE'),
        'eyopert': Text('E'),

        'apla': Key('escape, escape') + Text('{'),
        'anla': Key('escape, escape') + Text('}'),
        'sapla': Key('escape, escape') + Text('('),
        'sanla': Key('escape, escape') + Text(')'),

        'karen': Text('^'),
        'keratin': Text('0'),
        'doll': Text('$'),

        'ender': Key('end'),
        'homer': Key('home'),

        'screecare': Key('escape, escape') + Text('g^'),
        'screedoll': Key('escape, escape') + Text('g$'),

        'scree up': Key('escape, escape') + Text('gk'),
        'scree down': Key('escape, escape') + Text('gj'),

        'goron': Key('escape, escape, G'),

        'page high': Key('escape, escape') + Text('H'),
        'page low': Key('escape, escape') + Text('L'),

        # CamelCaseMotion plugin
        'calalope': Text(',b'),
        'calayope': Text(',w'),
        'end calayope': Text(',e'),
        'inner calalope': Text('i,b'),
        'inner calayope': Text('i,w'),
        'inner end calayope': Text('i,e'),

        # EasyMotion
        'easy lope': Key('%s:2, b' % LEADER),
        'easy yope': Key('%s:2, w' % LEADER),
        'easy elope': Key('%s:2, g, e' % LEADER),
        'easy iyope': Key('%s:2, e' % LEADER),

        'easy lopert': Key('%s:2, B' % LEADER),
        'easy yopert': Key('%s:2, W' % LEADER),
        'easy elopert': Key('%s:2, g, E' % LEADER),
        'easy eyopert': Key('%s:2, E' % LEADER),

        'warp': Text('``'),
        }

    for (spoken_object, command_object) in (('(lope | yope)', 'w'),
                                            ('(lopert | yopert)', 'W')):
        for (spoken_modifier, command_modifier) in (('inner', 'i'),
                                                    ('outer', 'a')):
            map_action = Text(command_modifier + command_object)
            mapping['%s %s' % (spoken_modifier, spoken_object)] = map_action
rulePrimitiveMotion = RuleRef(PrimitiveMotion(), name='PrimitiveMotion')


class UncountedMotion(MappingRule):
    mapping = {
        'tect': Text('%%'),
        'matu': Text('M'),
        }
ruleUncountedMotion = RuleRef(UncountedMotion(), name='UncountedMotion')


class MotionParameterMotion(MappingRule):
    mapping = {
        'phytic': 'f',
        'fitton': 'F',
        'pre phytic': 't',
        'pre fitton': 'T',
        }
ruleMotionParameterMotion = RuleRef(
    MotionParameterMotion(),
    name='MotionParameterMotion'
    )


class ParameterizedMotion(CompoundRule):
    spec = '<MotionParameterMotion> <LetterMapping>'
    extras = [ruleLetterMapping, ruleMotionParameterMotion]

    def value(self, node):
        children = node.children[0].children[0].children
        return Text(children[0].value() + children[1].value())
ruleParameterizedMotion = RuleRef(
    ParameterizedMotion(),
    name='ParameterizedMotion'
    )


class CountedMotion(NumericDelegateRule):
    spec = '[<count>] <motion>'
    extras = [ruleDigitalInteger[3],
              Alternative([
                  rulePrimitiveMotion,
                  ruleParameterizedMotion], name='motion')]
ruleCountedMotion = RuleRef(CountedMotion(), name='CountedMotion')


class Motion(CompoundRule):
    spec = '<motion>'
    extras = [Alternative(
        [ruleCountedMotion, ruleUncountedMotion],
        name='motion'
        )]

    def value(self, node):
        return node.children[0].children[0].children[0].value()

ruleMotion = RuleRef(Motion(), name='Motion')


# ****************************************************************************
# OPERATORS
# ****************************************************************************

_OPERATORS = {
    'relo': '',
    #'dell': 'd',
    'chaos': 'c',
    #'nab': 'y',
    'swap case': 'g~',
    'capital': 'gU',
    'lowery': 'gu',
    'external filter': '!',
    'external format': '=',
    'format text': 'gq',
    'rotate thirteen': 'g?',
    #'indent left': '<',
    #'indent right': '>',
    'define fold': 'zf',
    }


class PrimitiveOperator(MappingRule):
    mapping = dict((key, Text(val)) for (key, val) in _OPERATORS.iteritems())
    # tComment
    mapping['comm nop'] = Text('gc')
rulePrimitiveOperator = RuleRef(PrimitiveOperator(), name='PrimitiveOperator')


class Operator(NumericDelegateRule):
    spec = '[<count>] <PrimitiveOperator>'
    extras = [ruleDigitalInteger[3],
              rulePrimitiveOperator]
ruleOperator = RuleRef(Operator(), name='Operator')


class OperatorApplicationMotion(CompoundRule):
    spec = '[<Operator>] <Motion>'
    extras = [ruleOperator, ruleMotion]

    def value(self, node):
        children = node.children[0].children[0].children
        return_value = children[1].value()
        if children[0].value() is not None:
            return_value = children[0].value() + return_value
        return return_value
ruleOperatorApplicationMotion = RuleRef(
    OperatorApplicationMotion(),
    name='OperatorApplicationMotion'
    )


class OperatorSelfApplication(MappingRule):
    mapping = dict(('%s [<count>] %s' % (key, key), Text('%s%%(count)d%s' % (value, value)))
                   for (key, value) in _OPERATORS.iteritems())
    # tComment
    # string not action intentional dirty hack.
    mapping['comm nop [<count>] comm nop'] = 'tcomment'
    extras = [ruleDigitalInteger[3]]
    defaults = {'count': 1}

    def value(self, node):
        value = MappingRule.value(self, node)
        if value == 'tcomment':
            # ugly hack to get around tComment's not allowing ranges with gcc.
            value = node.children[0].children[0].children[0].children[1].value()
            if value in (1, '1', None):
                return Text('gcc')
            else:
                return Text('gc%dj' % (int(value) - 1))
        else:
            return value

ruleOperatorSelfApplication = RuleRef(
    OperatorSelfApplication(),
    name='OperatorSelfApplication'
    )

ruleOperatorApplication = Alternative([ruleOperatorApplicationMotion,
                                       ruleOperatorSelfApplication],
                                      name='OperatorApplication')


# ****************************************************************************
# COMMANDS
# ****************************************************************************


class PrimitiveCommand(MappingRule):
    mapping = {
        'flax': Key('X'),
        'switch': Key('escape, escape') + Key('s'),
        'undo': Key('u'),
        'redo': Key('c-r'),
#       'sundew': Key('c-z'),
#       'sundry': Key('cs-z'),
        'pesto': Key('escape, escape') + Key('P'),
        'post': Key('escape, escape') + Key('p'),
        'ditto': Text('.'),
        'ripple': 'macro',
        "visual": Key('escape, escape, v'),
        "visual line": Key('escape, escape') + Key("s-v"),
        "visual block": Key('escape, escape') + Key("c-v"),
        'dell': Key('escape, escape, d, d'),
        'yank': Key('escape, escape, y, y'),
        'deli': Key('d'),
        'yoink': Key('y'),
        "dello": Key('escape, escape, d, i, w'),
        "cello": Key('escape, escape, c, i, w'),
        'capsicum': Key('escape, escape, v, b, U, e, a'),
        #"indent left": Key("<"),
        #"indent right": Key(">")
        }

rulePrimitiveCommand = RuleRef(PrimitiveCommand(), name='PrimitiveCommand')


class Command(CompoundRule):
    spec = '[<count>] [reg <LetterMapping>] <command>'
    extras = [Alternative([ruleOperatorApplication,
                           rulePrimitiveCommand,
                           ], name='command'),
              ruleDigitalInteger[3],
              ruleLetterMapping]

    def value(self, node):
        delegates = node.children[0].children[0].children
        value = delegates[-1].value()
        prefix = ''
        if delegates[0].value() is not None:
            prefix += str(delegates[0].value())
        if delegates[1].value() is not None:
            # Hack for macros
            reg = delegates[1].value()[1]
            if value == 'macro':
                prefix += '@' + reg
                value = None
            else:
                prefix += "'" + reg
        if prefix:
            if value is not None:
                value = Text(prefix) + value
            else:
                value = Text(prefix)
        # TODO: ugly hack; should fix the grammar or generalize.
        if 'chaos' in zip(*node.results)[0]:
            return [('c', value), ('i', (NoAction(),) * 2)]
        else:
            return [('c', value)]
ruleCommand = RuleRef(Command(), name='Command')


# ****************************************************************************


class VimCommand(CompoundRule):
    spec = ('[<app>] [<literal>]')
    extras = [Repetition(Alternative([ruleCommand, RuleRef(Insertion())]), max=10, name='app'),
              RuleRef(LiteralIdentifierInsertion(), name='literal')]

    def _process_recognition(self, node, extras):
        insertion_buffer = []
        commands = []
        if 'app' in extras:
            for chunk in extras['app']:
                commands.extend(chunk)
        if 'literal' in extras:
            commands.extend(extras['literal'])
        for command in commands:
            mode, command = command
            if mode == 'i':
                insertion_buffer.append(command)
            else:
                execute_insertion_buffer(insertion_buffer)
                insertion_buffer = []
                command.execute(extras)
        execute_insertion_buffer(insertion_buffer)

grammar.add_rule(VimCommand())

grammar.load()


def unload():
    aenea.vocabulary.uninhibit_global_dynamic_vocabulary('vim', VIM_TAGS)
    for tag in VIM_TAGS:
        aenea.vocabulary.unregister_dynamic_vocabulary(tag)
    global grammar
    if grammar:
        grammar.unload()

    global ExModeGrammar
    if ExModeGrammar: ExModeGrammar.unload()

    ExModeGrammar = None
    grammar = None


###borrowed from https://github.com/davitenio/dragonfly-macros/blob/master/gvim.py

class ExModeEnabler(CompoundRule):
    # Spoken command to enable the ExMode grammar.
    spec = "execute"

    # Callback when command is spoken.
    def _process_recognition(self, node, extras):
        exModeBootstrap.disable()
        #normalModeGrammar.disable()
        ExModeGrammar.enable()
        Key("colon").execute()
        #print "ExMode grammar enabled"
        #print "Available commands:"
        #print '  \n'.join(ExModeCommands.mapping.keys())
        #print "\n(EX MODE)"



class ExModeDisabler(CompoundRule):
    # spoken command to exit ex mode
    spec = "<command>"
    extras = [Choice("command", {
        "kay": "okay",
        "cancel": "cancel",
    })]

    def _process_recognition(self, node, extras):
        ExModeGrammar.disable()
        exModeBootstrap.enable()
        #normalModeGrammar.enable()
        if extras["command"] == "cancel":
            #print "ex mode command canceled"
            Key("escape").execute()
        else:
            #print "ex mode command accepted"
            Key("enter").execute()
        #print "\n(NORMAL)"

# handles ExMode control structures
class ExModeCommands(MappingRule):
    mapping  = {
        "read": Text("r "),
        "(write|save) file": Text("w "),
        "quit": Text("q "),
        "turbo quit": Text("q! "),
        "write and quit": Text("wq "),
        "edit": Text("e "),
        "tab edit": Text("tabe "),

        "set number": Text("set number "),
        "set relative number": Text("set relativenumber "),
        "set ignore case": Text("set ignorecase "),
        "set no ignore case": Text("set noignorecase "),
        "set file format UNIX": Text("set fileformat=unix "),
        "set file format DOS": Text("set fileformat=dos "),
        "set file type Python": Text("set filetype=python"),
        "set file type tex": Text("set filetype=tex"),

        "P. W. D.": Text("pwd "),

        "help": Text("help"),
        "substitute": Text("s/"),
    }
    extras = [
        Dictation("text"),
        IntegerRef("n", 1, 50),
    ]
    defaults = {
        "n": 1,
}
              
# set up the grammar for vim's ex mode
exModeBootstrap = Grammar("ExMode bootstrap", context=vim_context)
exModeBootstrap.add_rule(ExModeEnabler())
exModeBootstrap.load()
ExModeGrammar = Grammar("ExMode grammar", context=vim_context)
ExModeGrammar.add_rule(ExModeCommands())
ExModeGrammar.add_rule(ExModeDisabler())
ExModeGrammar.load()
ExModeGrammar.disable()

