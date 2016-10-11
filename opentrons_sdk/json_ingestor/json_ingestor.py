from collections import OrderedDict
import itertools

from opentrons_sdk import containers
from opentrons_sdk.labware import instruments
from opentrons_sdk.robot import Robot


def interpret_json_protocol(json_protocol: OrderedDict):
    robot_deck = interpret_deck(json_protocol['deck'])
    robot_head = interpret_head(robot_deck, json_protocol['head'])
    interpret_instructions(robot_deck, robot_head, json_protocol['instructions'])


def interpret_deck(deck_info: OrderedDict):
    """
    "deck": {
        "p200-rack": {
            "labware": "tiprack-200ul",
            "slot" : "A1"
        },
        ".75 mL Tube Rack": {
            "labware": "tube-rack-.75ml",
            "slot" : "C1"
        },
        "trash": {
            "labware": "point",
            "slot" : "B2"
        }
    }
    :param protocol:
    :param deck_info:
    :return:
    """

    containers_data = {}
    for name, definition in deck_info.items():
        container_type = definition.get('labware')
        slot = definition.get('slot')
        container_obj = containers.load(container_type, slot, name)
        containers_data[name] = {'instance': container_obj}
    return containers_data


def interpret_head(robot_deck, head_dict: OrderedDict):

    """
    res example:
    { name: {
        'instance': ..,
        'settings': {'down-plunger-speed', '
        }
    }

    :param protocol:
    :param head_dict:
    :return:
    """

    SUPPORTED_TOOL_OPTIONS = {
        'tool',
        'tip-racks',
        'trash-container',
        'multi-channel',
        'axis',
        'volume',
        'down-plunger-speed',
        'up-plunger-speed',
        'tip-plunge',
        'extra-pull-volume',
        'extra-pull-delay',
        'distribute-percentage',
        'points'
    }


    head_obj = {}
    robot = Robot.get_instance()

    for tool_name, tool_config in head_dict.items():
        # Validate tool_config keys
        assert SUPPORTED_TOOL_OPTIONS >= set(tool_config.keys())
        tool_config.pop('tool')

        tool_instance = instruments.Pipette(
            name=tool_name,
            axis=tool_config.pop('axis'),
            min_volume=0,
            channels=(8 if tool_config.pop('multi-channel') else 1),
            )
        tool_instance.set_max_volume(tool_config.pop('volume'))

        # robot_containers = robot._deck.containers()
        tip_rack_objs = [
            robot_deck[item['container']]['instance']
            for item in tool_config.pop('tip-racks')
        ]
        tool_config['tip-racks'] = tip_rack_objs

        trash_obj = robot_deck[
            tool_config.pop('trash-container')['container']
        ]['instance']
        tool_config['trash-container'] = trash_obj

        tool_config['points'] = [dict(i) for i in tool_config.pop('points')]

        head_obj[tool_name] = {
            'instance': tool_instance,
            'settings': dict(tool_config)
        }
    return head_obj


def interpret_instructions(robot_deck, robot_head, instructions: list):
    """
    [
		{
			"tool" : "p10",
			"groups" : [
				{
					"transfer" : [
    					{
    						"from" : {
    							"container": "plate",
                                "location": "F1",
                                "touch-tip": false
    						},
    						"to": {
                            	"container" : "plate",
    							"location" : "A12",
    							"tip-offset" : 0,
    							"delay" : 0,
    							"touch-tip" : false
                            },
                            	"volume" : 10
						},
                        {
                            "from" : {
                                "container": "plate",
                                "location": "D1",
                                "touch-tip": false
                            },
                            "to": {
                                "container" : "plate",
                                "location" : "A2",
                                "tip-offset" : 0,
                                "delay" : 0,
                                "touch-tip" : false
                            },
                                "volume" : 10
                        }
					]
    :param robot_deck:
    :param robot_head:
    :param instructions:
    :return:
    """
    for instruction_dict in instructions:
        tool_name = instruction_dict.get('tool')
        tool_obj = robot_head[tool_name]['instance']
        trash_container = robot_head[tool_name]['settings']['trash-container']

        tips = itertools.cycle(
            itertools.chain(*robot_head[tool_name]['settings']['tip-racks'])
        )

        for group in instruction_dict.get('groups'):
            # We always pick up a new tip when entering a group
            tool_obj.pick_up_tip(next(tips))
            for command_type, commands_calls in group.items():
                handler = lambda args: handle_command(
                        tool_obj,robot_deck, robot_head, command_type, args
                    )
                [handler(command_arg) for command_arg in commands_calls]

            # LEAVING GROUP
            tool_obj.drop_tip(trash_container)


def handle_command(tool_obj, robot_deck, robot_head, command, command_args):
    SUPPORTED_COMMANDS = {
        'transfer': handle_transfer,
        'distribute': handle_distribute,
        'mix': handle_mix,
        'consolidate': handle_consolidate
    }

    if command not in SUPPORTED_COMMANDS:
        raise Exception('Unsupported COMMAND "{}" encountered'.format(command))
    return SUPPORTED_COMMANDS[command](
        tool_obj, robot_deck, robot_head, command_args
    )


def handle_transfer(tool_obj, robot_deck, robot_head, command_args):
    # print(tool_obj, robot_head, robot_deck, command_args)
    SUPPORTED_ARGS = {
        ''
    }
    from_info = command_args['from']
    from_container = robot_deck[from_info['container']]['instance']
    from_well = from_container[from_info['location']]
    should_touch_tip_on_from = from_info['touch-tip']

    to_info = command_args['to']
    to_container = robot_deck[to_info['container']]['instance']
    to_well = to_container[to_info['location']]
    should_touch_tip_on_to = to_info['touch-tip']

    volume = command_args.get('volume', tool_obj.max_volume)

    tool_obj.aspirate(volume, from_well)
    if should_touch_tip_on_from:
        tool_obj.touch_tip()

    tool_obj.dispense(volume, to_well)
    if should_touch_tip_on_to:
        tool_obj.touch_tip()


def handle_distribute(tool_obj, robot_deck, robot_head, command_args):
    pass



def handle_mix(tool_obj, robot_deck, robot_head, command_args):
    pass


def handle_consolidate(tool_obj, robot_deck, robot_head, command_args):
    pass