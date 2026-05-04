const {Zcl} = require('zigbee-herdsman');
const fz = require('zigbee-herdsman-converters/converters/fromZigbee');
const exposes = require('zigbee-herdsman-converters/lib/exposes');
const m = require('zigbee-herdsman-converters/lib/modernExtend');
const e = exposes.presets;
const ea = exposes.access;
const tuya = require('zigbee-herdsman-converters/lib/tuya');

const tzLocal = {
    ts0049_countdown: {
        key: ['water_countdown'],
        convertSet: async (entity, key, value, meta) => {
            const data = Buffer.alloc(5);
            data[0] = 0x0B;
            data.writeUInt32BE(value * 60, 1);  // minutes to seconds
            await entity.command(
                'manuSpecificTuyaE001',
                'setCountdown',
                {data},
            );
        },
    },
};

const fzLocal = {
    ts0049_countdown: {
        cluster: 'manuSpecificTuyaE001',
        type: 'raw',
        convert: (model, msg, publish, options, meta) => {
            const len = msg.data.length;
            const command = msg.data[2];
            if (len > 10 && command === 0x0a && msg.data[7] === 0x0b &&
                (msg.data[6] === 0x05 || msg.data[6] === 0x06)) {
                const value = msg.data.slice(8).readUInt32BE(0);
                return {water_countdown: value / 60};
            }
        },
    },
};

const definition = {
    fingerprint: [{modelID: 'TS0049', manufacturerName: '_TZ3000_XXXXXXXXX'}],
    model: "ZWV-YC2",
    vendor: "Tuya",
    description: 'Smart water valve with persistent timer',
    fromZigbee: [fz.battery, fzLocal.ts0049_countdown, tuya.fz.datapoints],
    toZigbee: [tzLocal.ts0049_countdown, tuya.tz.datapoints],
    configure: async (device, coordinatorEndpoint) => {
        await tuya.configureMagicPacket(device, coordinatorEndpoint);
    },
    extend: [
        m.deviceAddCustomCluster("manuSpecificTuyaE001", {
            name: "manuSpecificTuyaE001",
            ID: 0xe001,
            attributes: {},
            commands: {
                setCountdown: {
                    name: "setCountdown",
                    ID: 0xfe,
                    parameters: [{name: "data", type: 1008}],
                },
            },
            commandsResponse: {},
        }),
    ],
    exposes: [
        e.switch().withLabel('Valve'),
        e.numeric('countdown', ea.STATE_SET).withUnit('min').withValueMin(0).withValueMax(1440),
        e.numeric('valve_duration', ea.STATE).withUnit('s'),
        e.enum('valve_status', ea.STATE, ['manual', 'auto', 'idle']),
        e.numeric('battery', ea.STATE).withUnit('%').withValueMin(0).withValueMax(100),
        e.numeric('water_countdown', ea.STATE_SET).withUnit('minute').withValueMin(1).withValueMax(1440).withValueStep(1).withDescription('Persistent auto-off duration'),
    ],
    meta: {
        tuyaDatapoints: [
            [1,   'state',           tuya.valueConverter.onOff],
            [59,  'battery',         tuya.valueConverter.raw],
        ],
    },
};

module.exports = [definition];
