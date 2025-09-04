from yta_video_opengl.nodes.video.opengl import WavingNode
from yta_video_opengl.nodes.audio import ChorusNode
from yta_video_opengl.nodes import Node, TimedNode
from yta_validation.parameter import ParameterValidator
from yta_programming.decorators import singleton_old
from typing import Union

import moderngl


class _AudioEffects:
    """
    *For internal use only*

    The audio effects that will be available
    throught our internal _Effects class to
    wrap and make available all the audio
    effects we want to be available.
    """

    def __init__(
        self,
        effects: '_Effects'
    ):
        self._effects: _Effects = effects
        """
        The parent instance that includes this
        class instance as a property.
        """

    """
    Here below we expose all the effects
    we want the users to have available to
    be used.
    """
    def chorus(
        self,
        sample_rate: int,
        depth: int = 0,
        frequency: float = 0.25,
        start: Union[int, float, 'Fraction'] = 0,
        end: Union[int, float, 'Fraction', None] = None
    ):
        return _create_node(
            ChorusNode(
                sample_rate = sample_rate,
                depth = depth,
                frequency = frequency
            ),
            start = start,
            end = end
        )
    
    # TODO: Include definitive and tested audio
    # effects here below

class _VideoEffects:
    """
    *For internal use only*

    The video effects that will be available
    throught our internal _Effects class to
    wrap and make available all the video
    effects we want to be available.
    """

    def __init__(
        self,
        effects: '_Effects'
    ):
        self._effects: _Effects = effects
        """
        The parent instance that includes this
        class instance as a property.
        """

    """
    Here below we expose all the effects
    we want the users to have available to
    be used.
    """
    def waving_node(
        self,
        # TODO: Maybe 'frame_size' (?)
        size: tuple[int, int],
        amplitude: float = 0.05,
        frequency: float = 10.0,
        speed: float = 2.0,
        start: Union[int, float, 'Fraction'] = 0.0,
        end: Union[int, float, 'Fraction', None] = None
    ) -> 'TimedNode':
        """
        TODO: Explain this better.

        The 'start' and 'end' time moments are the
        limits of the time range in which the effect
        has to be applied to the frames inside that
        time range. Providing start=0 and end=None
        will make the effect to be applied to any
        frame.
        """
        return _create_node(
            WavingNode(
                context = self._effects._opengl_editor.context,
                size = size,
                amplitude = amplitude,
                frequency = frequency,
                speed = speed
            ),
            start = start,
            end = end
        )
    
    # TODO: Include definitive and tested video
    # effects here below

class _Effects:
    """
    *For internal use only*

    Class to be used within the OpenglEditor
    as a property to simplify the access to
    the effect nodes and also to have the
    single context always available through
    the OpenglEditor instance that is a 
    singleton one.

    Even though we can have more effects,
    this class is also the way we expose only
    the ones we actually want to expose to 
    the user.
    """
    
    def __init__(
        self,
        opengl_editor: 'OpenglEditor'
    ):
        self._opengl_editor: OpenglEditor = opengl_editor
        """
        The parent instance that includes this
        class instance as a property.
        """
        self.audio: _AudioEffects = _AudioEffects(self)
        """
        Shortcut to the audio effects that are
        available.
        """
        self.video: _VideoEffects = _VideoEffects(self)
        """
        Shortcut to the video effects that are
        available.
        """

@singleton_old
class OpenglEditor:
    """
    Singleton instance.

    It is a singleton instance to have a
    unique context for all the instances
    that need it and instantiate this
    class to obtain it. Here we group all
    the nodes we have available for the
    user.

    The GPU will make the calculations in
    parallel by itself, so we can handle a
    single context to make the nodes share
    textures and buffers.
    """

    def __init__(
        self
    ):
        self.context = moderngl.create_context(standalone = True)
        """
        The context that will be shared by all
        the nodes.
        """
        self.effects: _Effects = _Effects(self)
        """
        Shortcut to the effects.
        """
        # TODO: I should do something like
        # editor.effects.waving_node() to create
        # an instance of that effect node


def _create_node(
    node: Union['_AudioNode', '_VideoNode'],
    start: Union[int, float, 'Fraction'],
    end: Union[int, float, 'Fraction', None]
):
    # The class we pass has to inherit from this
    # 'Node' class, but could be other classes
    # in the middle, because an OpenglNode 
    # inherits from other class
    ParameterValidator.validate_mandatory_subclass_of('node', node, ['_AudioNode', '_VideoNode'])

    # We have to create a Node wrapper with the
    # time range in which it has to be applied
    # to all the frames.
    return TimedNode(
        node = node,
        start = start,
        end = end
    )

class _EffectStacked:
    """
    Class to wrap an effect that will be
    stacked with an specific priority.

    Priority is higher when lower value,
    and lower when higher value.
    """

    def __init__(
        self,
        effect: TimedNode,
        priority: int
    ):
        self.effect: TimedNode = effect
        """
        The effect to be applied.
        """
        self.priority: int = priority
        """
        The priority this stacked frame has versus
        the other stacked effects.
        """

# TODO: Move to another py file (?)
class EffectsStack:
    """
    Class to include a collection of effects
    we want to apply in some entity, that 
    will make easier to apply them.

    You can use this stack to keep the effects
    you want to apply on a Media or on the
    Timeline of your video editor.
    """

    @property
    def effects(
        self
    ) -> list[_EffectStacked]:
        """
        The effects but ordered from their 'start'
        time moment.
        """
        return sorted(self._effects, key = lambda effect: (effect.priority, effect.effect.start))
    
    @property
    def most_priority_effect(
        self
    ) -> _EffectStacked:
        """
        The effect with the highest priority,
        that is the lower priority value.
        """
        return min(self._effects, key = lambda effect: effect.priority)

    @property
    def less_priority_effect(
        self
    ) -> _EffectStacked:
        """
        The effect with the lowest priority,
        that is the biggest priority value.
        """
        return max(self._effects, key = lambda effect: effect.priority)
    
    def __init__(
        self
    ):
        self._effects: list[_EffectStacked] = []
        """
        A list containing all the effects that
        have been added to this stack, unordered.
        """

    def get_effects_for_t(
        self,
        t: Union[int, float, 'Fraction']
    ) -> list[TimedNode]:
        """
        Get the effects, ordered by priority
        and the 'start' field, that must be
        applied within the 't' time moment 
        provided because it is within the
        [start, end) time range.
        """
        return [
            effect.effect
            for effect in self.effects
            if effect.effect.is_within_time(t)
        ]

    def add_effect(
        self,
        effect: TimedNode,
        priority: Union[int, None] = None
    ) -> 'EffectsStack':
        """
        Add the provided 'effect' to the stack.
        """
        ParameterValidator.validate_mandatory_instance_of('effect', effect, TimedNode)

        # TODO: What about the same effect added
        # twice during the same time range? Can we
        # allow it? It will be applied twice for
        # specific 't' time moments but with 
        # different attributes. is it ok (?)

        # TODO: What if priority is already taken?
        # Should we let some effects have the same
        # priority (?)
        priority = (
            self.less_priority_effect.priority + 1
            if priority is None else
            priority
        )

        self._effects.append(_EffectStacked(
            effect = effect,
            priority = priority
        ))

        return self
    
    # TODO: Create 'remove_effect'