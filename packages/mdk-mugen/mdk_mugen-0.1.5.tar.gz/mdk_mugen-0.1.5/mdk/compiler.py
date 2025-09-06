from typing import Optional, Callable, Union
from functools import partial
import inspect
import copy
import traceback
import os

import mtl.project
from mtl.types.translation import ForwardParameter, StateDefinitionScope, StateScopeType as MtlScopeType
import mtlcc

from mdk.types.context import StateDefinition, TemplateDefinition, StateController, CompilerContext, StateScope, TriggerDefinition, StateScopeType, TranslationMode
from mdk.types.specifier import TypeSpecifier
from mdk.types.errors import CompilationException
from mdk.types.expressions import Expression
from mdk.types.builtins import IntType, StateNoType, BoolType
from mdk.types.defined import StateType, StateTypeT, MoveType, MoveTypeT, PhysicsType, PhysicsTypeT, FloatPairType, EnumType, FlagType

from mdk.utils.shared import convert, convert_tuple, format_bool, create_compiler_error
from mdk.utils.compiler import write_controller, rewrite_function

from mdk.stdlib.controllers import ChangeState

def build(def_file: str, output: str, run_mtl: bool = True, skip_templates: bool = False, locations: bool = True, compress: bool = False, preserve_ir: bool = False, target_folder: str = "mdk-out") -> None:
    context = CompilerContext.instance()
    try:
        output_path = os.path.join(os.path.abspath(os.path.dirname(def_file)), output)
        print(f"Will build state definitions to output path {output_path}.")
        ## builds the character from the input data.
        for state in context.statedefs:
            definition = context.statedefs[state]
            context.current_state = definition
            try:
                definition.fn() # this call registers the controllers in the statedef with the statedef itself.
            except Exception as exc:
                raise CompilationException(exc)
            context.current_state = None

        lib_groups = set()
        lib_targets: list[Callable | TypeSpecifier] = []
        if not skip_templates and len(context.templates) != 0:
            for t in context.templates:
                lib_targets.append(context.templates[t].fn)
                if context.templates[t].library == None:
                    context.templates[t].library = output + ".inc"
                lib_groups.add(context.templates[t].library)
        if not skip_templates and len(context.triggers) != 0:
            for t in context.triggers:
                lib_targets.append(context.triggers[t].fn)
                if context.triggers[t].library == None:
                    context.triggers[t].library = output + ".inc"
                lib_groups.add(context.triggers[t].library)
        if not skip_templates and len(context.typedefs) != 0:
            for t in context.typedefs:
                if not context.typedefs[t].register: continue
                lib_targets.append(context.typedefs[t])
                if context.typedefs[t].library == None:
                    context.typedefs[t].library = output + ".inc"
                lib_groups.add(context.typedefs[t].library)

        if len(lib_targets) > 0: 
            library(lib_targets, dirname = os.path.abspath(os.path.dirname(def_file)), locations = locations)
        
        with open(output, mode="w") as f:
            if not skip_templates and len(lib_groups) != 0:
                for group in lib_groups:
                    f.write("[Include]\n")
                    f.write(f"source = {group}\n")
            if not compress: f.write("\n")
            for name in context.statedefs:
                statedef = context.statedefs[name]
                f.write(f"[Statedef {name}]\n")
                for param in statedef.params:
                    f.write(f"{param} = {statedef.params[param].__str__()}\n")
                for local in statedef.locals:
                    f.write(f"local = {local.name} = {local.type.name}\n")
                if statedef.scope != None:
                    f.write(f"scope = {statedef.scope}\n")
                file_path = inspect.getsourcefile(statedef.fn)
                _, line_number = inspect.getsourcelines(statedef.fn)
                if locations:
                    f.write(f"mtl.location.file = {file_path}\n")
                    f.write(f"mtl.location.line = {line_number}\n")
                if not compress: f.write("\n")
                for controller in statedef.controllers:
                    write_controller(controller, f, locations)
                    if not compress: f.write("\n")
                if not compress: f.write("\n")

        ## read the DEF file (using MTL) and add the output to the statefile list,
        ## then re-export the DEF file.
        if run_mtl:
            print(f"Preparing to run MTL compiler for input project {def_file}.")
            project = mtl.project.loadDefinition(def_file)
            project.source_files.append(output)
            for global_variable in context.globals:
                scoped = StateDefinitionScope(MtlScopeType.SHARED, None)
                if global_variable.scope != None:
                    if global_variable.scope.scope == StateScopeType.PLAYER:
                        scoped = StateDefinitionScope(MtlScopeType.PLAYER, None)
                    if global_variable.scope.scope == StateScopeType.TARGET:
                        scoped = StateDefinitionScope(MtlScopeType.TARGET, None)
                    if global_variable.scope.scope == StateScopeType.HELPER:
                        scoped = StateDefinitionScope(MtlScopeType.HELPER, global_variable.scope.target)
                project.global_forwards.append(ForwardParameter(global_variable.name, global_variable.type.name, is_system = global_variable.is_system, scope = scoped))
            ## system globals
            project.global_forwards.append(ForwardParameter("mdk_internalTrigger", "int", is_system = False, scope = StateDefinitionScope(MtlScopeType.SHARED, None)))
            mtlcc.runCompilerFromDef(def_file, os.path.join(os.path.abspath(os.path.dirname(def_file)), target_folder), project)

        ## delete the output file if we're not preserving IR
        if not preserve_ir: 
            os.remove(output)
            for name in lib_groups:
                os.remove(name)
    except CompilationException as exc:
        create_compiler_error(exc)
    except Exception as exc:
        print("An internal error occurred while compiling a template, bug the developers.")
        raise exc

def library(inputs: list[Callable[..., None] | TypeSpecifier], dirname: str = "", output: Optional[str] = None, locations: bool = True, preserve_ir: bool = False) -> None:
    if len(inputs) == 0:
        raise Exception("Please specify some templates and/or triggers to be built.")
    context = CompilerContext.instance()
    try:
        per_file: dict[str, list[Union[TriggerDefinition, TemplateDefinition, TypeSpecifier]]] = {}
        for template in context.templates:
            definition = context.templates[template]
            context.current_template = definition
            kwargs = {}
            for param in definition.params:
                t = definition.params[param]
                kwargs[param] = Expression(param, t)
            try:
                definition.fn(**kwargs)
            except Exception as exc:
                raise CompilationException(exc)
            context.current_template = None
            if definition.library == None and output == None:
                raise CompilationException(f"Output library was not specified for template {definition.fn.__name__}, either specify a default output in call to library() or specify a library in the template() annotation.")
            if definition.library == None and output != None and definition.fn in inputs:
                definition.library = output
            if definition.library not in per_file:
                per_file[definition.library] = [] # type: ignore
            per_file[definition.library].append(definition) # type: ignore

        for trigger in context.triggers:
            definition = context.triggers[trigger]
            kwargs = {}
            for param in definition.params:
                t = definition.params[param]
                kwargs[param] = Expression(param, t)
            try:
                definition.exprn = definition.fn(**kwargs)
            except Exception as exc:
                raise CompilationException(exc)
            if definition.library == None and output != None and definition.fn in inputs:
                definition.library = output
            if definition.library not in per_file:
                per_file[definition.library] = [] # type: ignore
            per_file[definition.library].append(definition) # type: ignore

        for typedef in context.typedefs:
            definition = context.typedefs[typedef]
            if not definition.register:
                continue
            if not isinstance(definition, EnumType) and not isinstance(definition, FlagType):
                raise CompilationException(f"Can only emit type declarations for EnumType and FlagType, not {type(definition)}.")
            if definition.library == None and output != None and definition.fn in inputs:
                definition.library = output
            if definition.library not in per_file:
                per_file[definition.library] = [] # type: ignore
            per_file[definition.library].append(definition) # type: ignore

        for group in per_file:
            group_path = os.path.join(dirname, group)
            print(f"Creating output include file at path {group_path}.")
            with open(group_path, mode="w") as f:
                for definition in per_file[group]:
                    if isinstance(definition, TemplateDefinition):
                        f.write("[Define Template]\n")
                        f.write(f"name = {definition.fn.__name__}\n")
                        for local in definition.locals:
                            f.write(f"local = {local.name} = {local.type.name}\n")
                        file_path = inspect.getsourcefile(definition.fn)
                        _, line_number = inspect.getsourcelines(definition.fn)
                        if locations:
                            f.write(f"mtl.location.file = {file_path}\n")
                            f.write(f"mtl.location.line = {line_number}\n")
                        f.write("\n")
                        f.write("[Define Parameters]\n")
                        for param in definition.params:
                            f.write(f"{param} = {definition.params[param].name}\n")
                        f.write("\n")
                        for controller in definition.controllers:
                            write_controller(controller, f, locations)
                            f.write("\n")
                        f.write("\n")
                    elif isinstance(definition, TriggerDefinition):
                        f.write("[Define Trigger]\n")
                        f.write(f"name = {definition.fn.__name__}\n")
                        f.write(f"type = {definition.result.name}\n")
                        if not isinstance(definition.exprn, Expression):
                            raise Exception(f"Trigger definition {definition.fn.__name__} returned {type(definition.exprn)}, but must return Expression instead.")
                        f.write(f"value = {definition.exprn.exprn}\n")
                        file_path = inspect.getsourcefile(definition.fn)
                        _, line_number = inspect.getsourcelines(definition.fn)
                        if locations:
                            f.write(f"mtl.location.file = {file_path}\n")
                            f.write(f"mtl.location.line = {line_number}\n")
                        f.write("\n")
                        f.write("[Define Parameters]\n")
                        for param in definition.params:
                            f.write(f"{param} = {definition.params[param].name}\n")
                        f.write("\n")
                    elif isinstance(definition, TypeSpecifier):
                        f.write("[Define Type]\n")
                        f.write(f"name = {definition.name}\n")
                        if isinstance(definition, EnumType):
                            f.write(f"type = enum\n")
                            for member in definition.members:
                                f.write(f"enum = {member}\n")
                        elif isinstance(definition, FlagType):
                            f.write(f"type = flag\n")
                            for member in definition.members:
                                f.write(f"flag = {member}\n")
                        f.write("\n")
    except CompilationException as exc:
        create_compiler_error(exc)
    except Exception as exc:
        print("An internal error occurred while compiling a template, bug the developers.")
        raise exc
    
## very simple decorator to ensure a function called from a statedef
## can also have triggers applied correctly.
def statefunc(mode: TranslationMode = TranslationMode.STANDARD) -> Callable[[Callable[..., None]], Callable[..., None]]:
    def wrapped(fn: Callable[..., None]) -> Callable[..., None]:
        ctx = CompilerContext.instance()
        new_fn = rewrite_function(fn, mode = mode)
        ctx.statefuncs.append(fn.__name__)
        def inner(*args, **kwargs):
            new_fn(*args, **kwargs)
        return inner
    return wrapped

def statedef(
    type: Optional[StateType] = None,
    movetype: Optional[MoveType] = None,
    physics: Optional[PhysicsType] = None,
    anim: Optional[int] = None,
    velset: Optional[tuple[float, float]] = None,
    ctrl: Optional[bool] = None,
    poweradd: Optional[int] = None,
    juggle: Optional[int] = None,
    facep2: Optional[bool] = None,
    hitdefpersist: Optional[bool] = None,
    movehitpersist: Optional[bool] = None,
    hitcountpersist: Optional[bool] = None,
    sprpriority: Optional[int] = None,
    stateno: Optional[int] = None,
    scope: Optional[StateScope] = None,
    mode: TranslationMode = TranslationMode.STANDARD
) -> Callable[[Callable[[], None]], Callable[..., StateController]]:
    def decorator(fn: Callable[[], None]) -> Callable[..., StateController]:
        return create_statedef(fn, type, movetype, physics, anim, velset, ctrl, poweradd, juggle, facep2, hitdefpersist, movehitpersist, hitcountpersist, sprpriority, stateno, scope, mode)
    return decorator

## used by the @statedef decorator to create new statedefs,
## but can also be used by character developers to create statedefs ad-hoc (e.g. in a loop).
def create_statedef(
    fn: Callable[[], None],
    type: Optional[StateType] = None,
    movetype: Optional[MoveType] = None,
    physics: Optional[PhysicsType] = None,
    anim: Optional[int] = None,
    velset: Optional[tuple[float, float]] = None,
    ctrl: Optional[bool] = None,
    poweradd: Optional[int] = None,
    juggle: Optional[int] = None,
    facep2: Optional[bool] = None,
    hitdefpersist: Optional[bool] = None,
    movehitpersist: Optional[bool] = None,
    hitcountpersist: Optional[bool] = None,
    sprpriority: Optional[int] = None,
    stateno: Optional[int] = None,
    scope: Optional[StateScope] = None,
    mode: TranslationMode = TranslationMode.STANDARD
) -> Callable[..., StateController]:
    print(f"Discovered a new StateDef named {fn.__name__}. Will process and load this StateDef.")
    
    new_fn = rewrite_function(fn, mode = mode)
    statedef = StateDefinition(new_fn, {}, [], [], scope)

    # apply each parameter
    if stateno != None: statedef.params["id"] = Expression(str(stateno), IntType)
    if type != None:
        statedef.params["type"] = Expression(type.name, StateTypeT)
    if movetype != None:
        statedef.params["movetype"] = Expression(movetype.name, MoveTypeT)
    if physics != None:
        statedef.params["physics"] = Expression(physics.name, PhysicsTypeT)
    if anim != None: statedef.params["anim"] = Expression(str(anim), IntType)
    if velset != None: statedef.params["velset"] = convert_tuple(velset, FloatPairType)
    if ctrl != None: statedef.params["ctrl"] = format_bool(ctrl)
    if poweradd != None: statedef.params["poweradd"] = Expression(str(poweradd), IntType)
    if juggle != None: statedef.params["juggle"] = Expression(str(juggle), IntType)
    if facep2 != None: statedef.params["facep2"] = format_bool(facep2)
    if hitdefpersist != None: statedef.params["hitdefpersist"] = format_bool(hitdefpersist)
    if movehitpersist != None: statedef.params["movehitpersist"] = format_bool(movehitpersist)
    if hitcountpersist != None: statedef.params["hitcountpersist"] = format_bool(hitcountpersist)
    if sprpriority != None: statedef.params["sprpriority"] = Expression(str(sprpriority), IntType)

    # add the new statedef to the context
    ctx = CompilerContext.instance()
    if fn.__name__ in ctx.statedefs:
        raise Exception(f"Attempted to overwrite statedef with name {fn.__name__}.")
    ctx.statedefs[fn.__name__] = statedef

    return partial(ChangeState, value = fn.__name__)

def do_template(name: str, validator: Optional[Callable[..., dict[str, Expression]]], *args, **kwargs) -> StateController:
    def generic_template(*args, **kwargs) -> StateController:
        if len(args) != 0:
            raise Exception("Templates cannot be called with positional arguments, only keyword arguments.")
        ## if a validator was provided, we give the template author a chance to validate and even modify input arguments.
        if validator != None and (kwargs := validator(**kwargs)) == None:
            raise Exception(f"Could not place call to template with name {name}, template validation check failed.")
        context = CompilerContext.instance()

        ## need to check for any StateNoType inputs
        target_template = context.templates[name]

        new_controller = StateController()
        new_controller.type = name
        new_controller.params = {}
        for arg in kwargs:
            target_type = target_template.params[arg]
            next_arg = kwargs[arg]
            if target_type == StateNoType and isinstance(next_arg, partial):
                new_controller.params[arg] = Expression(next_arg.keywords["value"], StateNoType)
            elif target_type == StateNoType and isinstance(next_arg, Callable):
                new_controller.params[arg] = Expression(next_arg.__name__, StateNoType)
            else:
                new_controller.params[arg] = kwargs[arg]
        if len(context.trigger_stack) != 0 or len(context.if_stack) != 0:
            new_controller.triggers = copy.deepcopy(context.trigger_stack)
            if len(context.if_stack) != 0:
                new_controller.triggers.append(Expression(f"mdk_internalTrigger = {context.if_stack[-1]}", BoolType))
            if len(context.check_stack) != 0:
                new_controller.triggers = copy.deepcopy(context.check_stack) + new_controller.triggers
                context.check_stack = []
        else:
            new_controller.triggers = [format_bool(True)]
        ## i believe this should always be right, since it flows from <callsite> -> do_template -> generic_template
        callsite = traceback.extract_stack()[-3]
        new_controller.location = (callsite.filename, callsite.lineno if callsite.lineno != None else 0)
        return new_controller
    ctrl = generic_template(*args, **kwargs)
    ctrl.type = name
    context = CompilerContext.instance()
    if context.current_state != None:
        context.current_state.controllers.append(ctrl)
    elif context.current_template != None:
        context.current_template.controllers.append(ctrl)
    return ctrl

def do_trigger(name: str, validator: Optional[Callable[..., dict[str, Expression]]], *args, **kwargs) -> Expression:
    if len(kwargs) != 0:
        raise Exception("Triggers cannot be called with keyword arguments, only positional arguments.")
    ## if a validator was provided, we give the trigger author a chance to validate and even modify input arguments.
    if validator != None and (args := validator(*args)) == None:
        raise Exception(f"Could not place call to trigger with name {name}, trigger validation check failed.")
    context = CompilerContext.instance()
    param_string = ", ".join([convert(arg).exprn for arg in args])
    ## just trust the output type. the MTL side will do final type validation during trigger replacement.
    return Expression(f"{name}({param_string})", context.triggers[name].result)

def template(inputs: list[TypeSpecifier] = [], library: Optional[str] = None, validator: Optional[Callable[..., dict[str, Expression]]] = None) -> Callable[[Callable[..., None]], Callable[..., StateController]]:
    def decorator(fn: Callable[..., None]) -> Callable[..., StateController]:
        print(f"Discovered a new Template named {fn.__name__}. Will process and load this Template.")
        # get params of decorated function
        signature = inspect.signature(fn)

        # create new function with ast fixes
        new_fn = rewrite_function(fn)

        # ensure parameters align
        if len(signature.parameters) != len(inputs):
            raise Exception(f"Mismatch in template parameter count: saw {len(inputs)} input types, and {len(signature.parameters)} real parameters.")

        params: dict[str, TypeSpecifier] = {}
        index = 0
        for param in signature.parameters:
            params[param] = inputs[index]
            index += 1
        template = TemplateDefinition(new_fn, library, params, [], [])

        # add the new template to the context
        ctx = CompilerContext.instance()
        if fn.__name__ in ctx.templates:
            raise Exception(f"Attempted to overwrite template with name {fn.__name__}.")
        ctx.templates[fn.__name__] = template

        return partial(do_template, fn.__name__, validator)
    return decorator

def trigger(inputs: list[TypeSpecifier], result: TypeSpecifier, library: Optional[str] = None, validator: Optional[Callable[..., dict[str, Expression]]] = None) -> Callable[[Callable[..., Expression]], Callable[..., Expression]]:
    def decorator(fn: Callable[..., Expression]) -> Callable[..., Expression]:
        print(f"Discovered a new Trigger named {fn.__name__}. Will process and load this Trigger.")
        # get params of decorated function
        signature = inspect.signature(fn)

        # create new function with ast fixes
        ## note: triggers cannot overload print functions (because triggers can't contain controllers).
        new_fn = rewrite_function(fn, overload_print = False) # type: ignore

        # ensure parameters align
        if len(signature.parameters) != len(inputs):
            raise Exception(f"Mismatch in trigger parameter count: saw {len(inputs)} input types, and {len(signature.parameters)} real parameters.")

        params: dict[str, TypeSpecifier] = {}
        index = 0
        for param in signature.parameters:
            params[param] = inputs[index]
            index += 1

        trigger = TriggerDefinition(new_fn, library, result, params) # type: ignore

        # add the new template to the context
        ctx = CompilerContext.instance()
        if fn.__name__ in ctx.triggers:
            raise Exception(f"Attempted to overwrite trigger with name {fn.__name__}.")
        ctx.triggers[fn.__name__] = trigger

        return partial(do_trigger, fn.__name__, validator)
    return decorator

class ControllerProps:
    def __init__(self, ignorehitpause: Expression | bool | None = None, persistent: Expression | int | None = None):
        self.ignorehitpause = convert(ignorehitpause) if ignorehitpause != None else None
        self.persistent = convert(persistent) if persistent != None else None
        self.prev_state = (None, None)
    def __enter__(self):
        context = CompilerContext.instance()
        self.prev_state = context.default_state
        context.default_state = (self.ignorehitpause, self.persistent)
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        context = CompilerContext.instance()
        context.default_state = self.prev_state
        return False
    
__all__ = ["build", "library", "statedef", "create_statedef", "template", "trigger"]