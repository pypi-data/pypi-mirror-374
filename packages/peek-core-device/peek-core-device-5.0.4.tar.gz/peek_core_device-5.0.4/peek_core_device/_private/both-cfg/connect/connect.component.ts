import { takeUntil } from "rxjs/operators";
import { Component, OnInit } from "@angular/core";
import { BalloonMsgService, HeaderService } from "@synerty/peek-plugin-base-js";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import {
    DeviceServerService,
    DeviceTupleService,
    ServerInfoTuple,
} from "@peek/peek_core_device/_private";
import { DeviceTypeEnum } from "@peek/peek_core_device/_private/hardware-info/hardware-info";

@Component({
    selector: "peek-core-device-cfg-connect",
    templateUrl: "connect.component.web.html",
})
export class ConnectComponent extends NgLifeCycleEvents implements OnInit {
    protected server: ServerInfoTuple = new ServerInfoTuple();
    protected httpPortStr: string = "";
    protected websocketPortStr: string = "";
    protected deviceType: DeviceTypeEnum;
    protected isWeb: boolean;

    constructor(
        private balloonMsg: BalloonMsgService,
        private headerService: HeaderService,
        private tupleService: DeviceTupleService,
        private deviceServerService: DeviceServerService,
    ) {
        super();
        this.httpPortStr = this.server.httpPort.toString();
        this.websocketPortStr = this.server.websocketPort.toString();

        this.deviceType = this.tupleService.hardwareInfo.deviceType();
        this.isWeb = this.tupleService.hardwareInfo.isWeb();

        this.deviceServerService.connInfoObserver
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((info: ServerInfoTuple) => {
                this.server = info;
                this.httpPortStr = this.server.httpPort.toString();
                this.websocketPortStr = this.server.websocketPort.toString();
            });

        this.server = this.deviceServerService.connInfo;
    }

    override ngOnInit() {}

    connectEnabled(): boolean {
        if (this.server != null) {
            if (this.server.host == null || !this.server.host.length)
                return false;

            if (!parseInt(this.websocketPortStr)) return false;

            if (!parseInt(this.httpPortStr)) return false;
        }
        return true;
    }

    saveClicked() {
        try {
            this.server.httpPort = parseInt(this.httpPortStr);
            this.server.websocketPort = parseInt(this.websocketPortStr);
        } catch (e) {
            this.balloonMsg.showError("Port numbers must be integers.");
            return;
        }

        this.deviceServerService.setServer(this.server).then(() => {
            this.balloonMsg.showSuccess("Peek server has been updated");
        });
    }

    setUseSsl(val: boolean) {
        this.server.useSsl = val;
    }
}
