from .handle_path import scan_dir, find_in_path
import sys
import traceback
import importlib
import builtins

major, minor = sys.version_info[:2]

original_import = builtins.__import__
_CHILD_ERR_MSG = 'module {!r} has no child module {!r}'
def custom_import(name, globals=None, locals=None, fromlist=(), level=0):
    try:
        return original_import(name,
                               globals=globals,
                               locals=locals,
                               fromlist=fromlist,
                               level=level)
    except ModuleNotFoundError as e:
        if " halted; None in sys.modules" not in e.msg:
            parent, _, child = e.name.rpartition('.')            
            if parent:
                original_msg = e.msg
                e.msg = _CHILD_ERR_MSG.format(parent, child)
                if original_msg.endswith("is not a package"):
                    e.msg += f'; {parent!r} is not a package'
                e.args = (e.msg,)
        raise

builtins.__import__ = custom_import

importlib._bootstrap.BuiltinImporter.__find__ = staticmethod(lambda name=None: (sorted(sys.builtin_module_names) if not name else []))

def _compute_suggestion_error(exc_value, tb, wrong_name):
    if wrong_name is None or not isinstance(wrong_name, str):
        return None
    if isinstance(exc_value, AttributeError):
        obj = exc_value.obj
        try:
            try:
                d = dir(obj)
            except TypeError:  # Attributes are unsortable, e.g. int and str
                d = list(obj.__class__.__dict__.keys()) + list(obj.__dict__.keys())
            d = sorted([x for x in d if isinstance(x, str)])
            hide_underscored = (wrong_name[:1] != '_')
            if hide_underscored and tb is not None:
                while tb.tb_next is not None:
                    tb = tb.tb_next
                frame = tb.tb_frame
                if 'self' in frame.f_locals and frame.f_locals['self'] is obj:
                    hide_underscored = False
            if hide_underscored:
                d = [x for x in d if x[:1] != '_']
        except Exception:
            return _handle_module(exc_value)
    elif isinstance(exc_value, ImportError):
        if isinstance(exc_value, ModuleNotFoundError):
            return _handle_module(exc_value)
        try:
            mod = __import__(exc_value.name)
            try:
                d = dir(mod)
            except TypeError:  # Attributes are unsortable, e.g. int and str
                d = list(mod.__dict__.keys())
            d = sorted([x for x in d if isinstance(x, str)])
            if wrong_name[:1] != '_':
                d = [x for x in d if x[:1] != '_']
        except Exception:
            return None
    else:
        assert isinstance(exc_value, NameError)
        # find most recent frame
        if tb is None:
            return None
        while tb.tb_next is not None:
            tb = tb.tb_next
        frame = tb.tb_frame
        d = (
            list(frame.f_locals)
            + list(frame.f_globals)
            + list(frame.f_builtins)
        )
        d = [x for x in d if isinstance(x, str)]

        # Check first if we are in a method and the instance
        # has the wrong name as attribute
        if 'self' in frame.f_locals:
            self = frame.f_locals['self']
            try:
                has_wrong_name = hasattr(self, wrong_name)
            except Exception:
                has_wrong_name = False
            if has_wrong_name:
                return f"self.{wrong_name}"

    suggestion = _calculate_closed_name(wrong_name, d)
    if minor >= 15:
        # If no direct attribute match found, check for nested attributes
        from contextlib import suppress
        from traceback import _check_for_nested_attribute
        if not suggestion and isinstance(exc_value, AttributeError):
            with suppress(Exception):
                nested_suggestion = _check_for_nested_attribute(exc_value.obj, wrong_name, d)
                if nested_suggestion:
                    return nested_suggestion

    return suggestion

try:
    _MAX_STRING_SIZE = traceback._MAX_STRING_SIZE
    _MAX_CANDIDATE_ITEMS = traceback._MAX_CANDIDATE_ITEMS
    _MOVE_COST = traceback._MOVE_COST
    _CASE_COST = traceback._CASE_COST
except:
    _MAX_CANDIDATE_ITEMS = 750
    _MAX_STRING_SIZE = 40
    _MOVE_COST = 2
    _CASE_COST = 1

def _handle_module(exc_value):
    if not isinstance(exc_value, ModuleNotFoundError):
        return    
    all_result = []
    parent, _, child = exc_value.name.rpartition('.')
    if len(child) > _MAX_STRING_SIZE:
        return
    suggest_list = []
    for i in sys.meta_path:
        try:
            func = getattr(i, '__find__', None)
            if callable(func):
                list_d = func(parent)
                if list_d:
                    suggest_list.append(list_d)
        except:
            pass
    if not parent:
        for paths in sys.path:
            suggest_list.append(scan_dir(paths))
    else:
        suggest_list.append(find_in_path(parent))
    for i in suggest_list:
        if child in i:
            return child
        result = _calculate_closed_name(child, i)
        if result:
            all_result.append(result)
    return _calculate_closed_name(child, sorted(all_result))

try:
    _levenshtein_distance = traceback._levenshtein_distance
except Exception:
    def _levenshtein_distance(a, b, max_cost):
        # A Python implementation of Python/suggestions.c:levenshtein_distance.

        # Both strings are the same
        if a == b:
            return 0

        # Trim away common affixes
        pre = 0
        while a[pre:] and b[pre:] and a[pre] == b[pre]:
            pre += 1
        a = a[pre:]
        b = b[pre:]
        post = 0
        while a[:post or None] and b[:post or None] and a[post-1] == b[post-1]:
            post -= 1
        a = a[:post or None]
        b = b[:post or None]
        if not a or not b:
            return _MOVE_COST * (len(a) + len(b))
        if len(a) > _MAX_STRING_SIZE or len(b) > _MAX_STRING_SIZE:
            return max_cost + 1

        # Prefer shorter buffer
        if len(b) < len(a):
            a, b = b, a

        # Quick fail when a match is impossible
        if (len(b) - len(a)) * _MOVE_COST > max_cost:
            return max_cost + 1

        # Instead of producing the whole traditional len(a)-by-len(b)
        # matrix, we can update just one row in place.
        # Initialize the buffer row
        row = list(range(_MOVE_COST, _MOVE_COST * (len(a) + 1), _MOVE_COST))

        result = 0
        for bindex in range(len(b)):
            bchar = b[bindex]
            distance = result = bindex * _MOVE_COST
            minimum = sys.maxsize
            for index in range(len(a)):
                # 1) Previous distance in this row is cost(b[:b_index], a[:index])
                substitute = distance + _substitution_cost(bchar, a[index])
                # 2) cost(b[:b_index], a[:index+1]) from previous row
                distance = row[index]
                # 3) existing result is cost(b[:b_index+1], a[index])

                insert_delete = min(result, distance) + _MOVE_COST
                result = min(insert_delete, substitute)

                # cost(b[:b_index+1], a[:index+1])
                row[index] = result
                if result < minimum:
                    minimum = result
            if minimum > max_cost:
                # Everything in this row is too big, so bail early.
                return max_cost + 1
        return result

    def _substitution_cost(ch_a, ch_b):
        if ch_a == ch_b:
            return 0
        if ch_a.lower() == ch_b.lower():
            return _CASE_COST
        return _MOVE_COST

def _calculate_closed_name(wrong_name, d):
    try:
        import _suggestions
    except ImportError:
        pass
    else:
        return _suggestions._generate_suggestions(d, wrong_name)

    # Compute closest match

    if len(d) > _MAX_CANDIDATE_ITEMS:
        return None
    wrong_name_len = len(wrong_name)
    if wrong_name_len > _MAX_STRING_SIZE:
        return None
    best_distance = wrong_name_len
    suggestion = None
    for possible_name in d:
        if possible_name == wrong_name:
            # A missing attribute is "found". Don't suggest it (see GH-88821).
            continue
        # No more than 1/3 of the involved characters should need changed.
        max_distance = (len(possible_name) + wrong_name_len + 3) * _MOVE_COST // 6
        # Don't take matches we've already beaten.
        max_distance = min(max_distance, best_distance - 1)
        current_distance = _levenshtein_distance(wrong_name, possible_name, max_distance)
        if current_distance > max_distance:
            continue
        if not suggestion or current_distance < best_distance:
            suggestion = possible_name
            best_distance = current_distance
    return suggestion

StackSummary = traceback.StackSummary
_walk_tb_with_full_positions = traceback._walk_tb_with_full_positions
_safe_string = traceback._safe_string
TracebackException = traceback.TracebackException

def new_init(self, exc_type, exc_value, exc_traceback, *, limit=None,
            lookup_lines=True, capture_locals=False, compact=False,
            max_group_width=15, max_group_depth=10, save_exc_type=True, _seen=None):
    # NB: we need to accept exc_traceback, exc_value, exc_traceback to
    # permit backwards compat with the existing API, otherwise we
    # need stub thunk objects just to glue it together.
    # Handle loops in __cause__ or __context__.
    is_recursive_call = _seen is not None
    if _seen is None:
        _seen = set()
    _seen.add(id(exc_value))

    self.max_group_width = max_group_width
    self.max_group_depth = max_group_depth

    self.stack = StackSummary._extract_from_extended_frame_gen(
            _walk_tb_with_full_positions(exc_traceback),
            limit=limit, lookup_lines=lookup_lines,
            capture_locals=capture_locals)

    self._exc_type = exc_type if save_exc_type else None
    if minor <= 12:
        self.exc_type = exc_type    

    # Capture now to permit freeing resources: only complication is in the
    # unofficial API _format_final_exc_line
    self._str = _safe_string(exc_value, 'exception')
    try:
        self.__notes__ = getattr(exc_value, '__notes__', None)
    except Exception as e:
        notes = "__notes__"
        self.__notes__ = [
            f'Ignored error getting __notes__: {_safe_string(e, notes, repr)}']

    self._is_syntax_error = False
    self._have_exc_type = exc_type is not None
    if exc_type is not None:
        self.exc_type_qualname = exc_type.__qualname__
        self.exc_type_module = exc_type.__module__
    else:
        self.exc_type_qualname = None
        self.exc_type_module = None

    if exc_type and issubclass(exc_type, SyntaxError):
        # Handle SyntaxError's specially
        self.filename = exc_value.filename
        lno = exc_value.lineno
        self.lineno = str(lno) if lno is not None else None
        end_lno = exc_value.end_lineno
        self.end_lineno = str(end_lno) if end_lno is not None else None
        self.text = exc_value.text
        self.offset = exc_value.offset
        self.end_offset = exc_value.end_offset
        self.msg = exc_value.msg
        self._is_syntax_error = True
    elif exc_type and issubclass(exc_type, ModuleNotFoundError) and \
            getattr(exc_value, "name", None) and \
            "None in sys.modules" not in self._str and \
            "is not a package" not in self._str:
        wrong_name = getattr(exc_value, "name", None)
        parent, _, child = wrong_name.rpartition('.')
        suggestion = _compute_suggestion_error(exc_value, exc_traceback, wrong_name)
        if suggestion == child:
            self._str += ", but it appear in the final result from '__find__'. Is your code wrong?"
        elif suggestion:
            self._str += f". Did you mean: '{suggestion}'?"
        if minor >= 15:
            top = wrong_name.partition('.')[0]
            if sys.flags.no_site and not parent and top not in sys.stdlib_module_names:
                if not self._str.endswith('?'):
                    self._str += "."
                self._str += (" Site initialization is disabled, did you forget to "
                + "add the site-packages directory to sys.path?")
    elif minor not in (10, 11):
        if exc_type and issubclass(exc_type, ImportError) and \
                getattr(exc_value, "name_from", None) is not None:
            wrong_name = getattr(exc_value, "name_from", None)
            suggestion = _compute_suggestion_error(exc_value, exc_traceback, wrong_name)
            if suggestion:
                self._str += f". Did you mean: '{suggestion}'?"    
        elif exc_type and issubclass(exc_type, (NameError, AttributeError)) and \
                getattr(exc_value, "name", None) is not None:
            wrong_name = getattr(exc_value, "name", None)
            suggestion = _compute_suggestion_error(exc_value, exc_traceback, wrong_name)
            if suggestion:
                self._str += f". Did you mean: '{suggestion}'?"
            if issubclass(exc_type, NameError):
                wrong_name = getattr(exc_value, "name", None)
                if wrong_name is not None and wrong_name in sys.stdlib_module_names:
                    if suggestion:
                        self._str += f" Or did you forget to import '{wrong_name}'?"
                    else:
                        self._str += f". Did you forget to import '{wrong_name}'?"
    if lookup_lines:
        self._load_lines()
    self.__suppress_context__ = \
            exc_value.__suppress_context__ if exc_value is not None else False

    # Convert __cause__ and __context__ to `TracebackExceptions`s, use a
    # queue to avoid recursion (only the top-level call gets _seen == None)
    if not is_recursive_call:
        queue = [(self, exc_value)]
        while queue:
            te, e = queue.pop()
            if (e is not None and e.__cause__ is not None
                    and id(e.__cause__) not in _seen):
                cause = TracebackException(
                        type(e.__cause__),
                        e.__cause__,
                        e.__cause__.__traceback__,
                        limit=limit,
                        lookup_lines=lookup_lines,
                        capture_locals=capture_locals,
                        max_group_width=max_group_width,
                        max_group_depth=max_group_depth,
                        _seen=_seen)
            else:
                cause = None

            if compact:
                need_context = (cause is None and
                                    e is not None and
                                    not e.__suppress_context__)
            else:
                need_context = True
            if (e is not None and e.__context__ is not None
                    and need_context and id(e.__context__) not in _seen):
                context = TracebackException(
                        type(e.__context__),
                        e.__context__,
                        e.__context__.__traceback__,
                        limit=limit,
                        lookup_lines=lookup_lines,
                        capture_locals=capture_locals,
                        max_group_width=max_group_width,
                        max_group_depth=max_group_depth,
                        _seen=_seen)
            else:
                context = None

            if e is not None and isinstance(e, BaseExceptionGroup):
                exceptions = []
                for exc in e.exceptions:
                        texc = TracebackException(
                            type(exc),
                            exc,
                            exc.__traceback__,
                            limit=limit,
                            lookup_lines=lookup_lines,
                            capture_locals=capture_locals,
                            max_group_width=max_group_width,
                            max_group_depth=max_group_depth,
                            _seen=_seen)
                        exceptions.append(texc)
            else:
                exceptions = None

            te.__cause__ = cause
            te.__context__ = context
            te.exceptions = exceptions
            if cause:
                queue.append((te.__cause__, e.__cause__))
            if context:
                queue.append((te.__context__, e.__context__))
            if exceptions:
                queue.extend(zip(te.exceptions, e.exceptions))

TracebackException.__init__ = new_init
