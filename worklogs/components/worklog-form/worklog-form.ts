import {
    Component,
    EventEmitter,
    Input,
    OnChanges,
    Output,
    SimpleChanges,
    inject
} from '@angular/core';

import {
    CommonModule
} from '@angular/common';

import {
    ReactiveFormsModule,
    FormBuilder,
    Validators
} from '@angular/forms';

import {
    ProjectModel
} from '../../../profile/models/project';

import {
    CategoryModel
} from '../../../profile/models/category';

import {
    WorkLogModel
} from '../../models/worklog';

@Component({

    selector:'app-worklog-form',

    standalone:true,

    imports:[

        CommonModule,

        ReactiveFormsModule

    ],

    templateUrl:'./worklog-form.html',

    styleUrl:'./worklog-form.scss'

})
export class WorkLogForm
implements OnChanges{

    @Input()

    worklog:WorkLogModel|null=null;

    @Input()

    projects:ProjectModel[]=[];

    @Input()

    categories:CategoryModel[]=[];

    @Output()

    save=
    new EventEmitter<any>();

    @Output()

    close=
    new EventEmitter<void>();

    private fb=
    inject(FormBuilder);

    form=this.fb.group({

        project_id:[null],

        category_id:[null],

        title:[''],

        notes:[
            '',
            Validators.required
        ],

        work_date:[
            new Date().toISOString().substring(0,10),
            Validators.required
        ],

        hours:[
            0,
            Validators.min(0)
        ],

        minutes:[
            0,
            [
                Validators.min(0),
                Validators.max(59)
            ]
        ]

    });

    ngOnChanges(
        changes:SimpleChanges
    ):void{

        if(!this.worklog){

            this.form.reset({

                project_id:null,

                category_id:null,

                title:'',

                notes:'',

                work_date:new Date().toISOString().substring(0,10),

                hours:0,

                minutes:0

            });

            return;

        }

        const parts=this.worklog.duration?.split(':') ?? ['0','0'];

        this.form.patchValue({

            project_id:this.worklog.project_id,

            category_id:this.worklog.category_id,

            title:this.worklog.title,

            notes:this.worklog.notes,

            work_date:this.worklog.work_date,

            hours:Number(parts[0]),

            minutes:Number(parts[1])

        });

    }

    submit():void{

        if(this.form.invalid){

            this.form.markAllAsTouched();

            return;

        }

        const value=this.form.getRawValue();

        this.save.emit({

            project_id:value.project_id,

            category_id:value.category_id,

            title:value.title?.trim(),

            notes:value.notes?.trim(),

            work_date:value.work_date,

            duration:
                `${value.hours}:${value.minutes}`

        });

    }

}
