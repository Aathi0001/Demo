import {
    Component,
    EventEmitter,
    Input,
    Output
} from '@angular/core';

import {
    CommonModule
} from '@angular/common';

import {
    WorkLogModel
} from '../../models/worklog';

@Component({

    selector:'app-worklog-card',

    standalone:true,

    imports:[
        CommonModule
    ],

    templateUrl:'./worklog-card.html',

    styleUrl:'./worklog-card.scss'

})
export class WorkLogCard {

    @Input()

    worklog!: WorkLogModel;

    @Output()

    open =
    new EventEmitter<void>();

    @Output()

    menu =
    new EventEmitter<MouseEvent>();

    pressTimer:any;

    startPress(event:TouchEvent){

        this.pressTimer=setTimeout(()=>{

            const touch=event.touches[0];

            this.menu.emit({

                clientX:touch.clientX,

                clientY:touch.clientY,

                preventDefault(){},
                stopPropagation(){}

            } as MouseEvent);

        },500);

    }

    stopPress(){

        clearTimeout(this.pressTimer);

    }

}
