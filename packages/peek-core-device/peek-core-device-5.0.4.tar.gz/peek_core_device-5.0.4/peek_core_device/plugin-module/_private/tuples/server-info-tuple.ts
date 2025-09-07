import { addTupleType, Tuple } from "@synerty/vortexjs";
import { deviceTuplePrefix } from "@peek/peek_core_device/_private/PluginNames";

@addTupleType
export class ServerInfoTuple extends Tuple {
    public static readonly tupleName = deviceTuplePrefix + "ServerInfoTuple";

    host: string = null;
    useSsl: boolean = false;
    httpPort: number = 8000;
    websocketPort: number = 8000;
    hasConnected: boolean = false;

    constructor() {
        super(ServerInfoTuple.tupleName);
    }

    async loadDefaultValues(): Promise<void> {
        try {
            console.log(`ServerInfoTuple: Fetching server-info-tuple asset`);
            const response = await fetch(
                "/assets/peek_core_device/server-info-tuple-defaults.json",
            );

            if (!response.ok) {
                console.log(
                    `ServerInfoTuple: Failed to load defaults:` +
                        ` ${response.status} ${response.statusText}`,
                );
                return;
            }

            const defaults: any = await response.json();

            if (defaults == null) {
                console.log(
                    `ServerInfoTuple: Fetched empty server-info-tuple asset`,
                );
                return;
            }

            this.host = defaults["host"];
            this.useSsl = defaults["useSsl"];
            this.httpPort = defaults["httpPort"];
            this.websocketPort = defaults["websocketPort"];
            this.hasConnected = defaults["hasConnected"];

            console.log(`ServerInfoTuple: Successfully loaded asset: ${defaults}`);
        } catch (e) {
            console.log(
                `ServerInfoTuple: Can not fetch server-info-tuple: ${e}`,
            );
            return;
        }
    }
}
