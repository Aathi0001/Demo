import {
    Component,
    EventEmitter,
    Input,
    OnInit,
    Output,
    inject
} from '@angular/core';

import {
    CommonModule
} from '@angular/common';

import {
    ReactiveFormsModule,
    FormBuilder
} from '@angular/forms';

import {
    debounceTime,
    distinctUntilChanged
} from 'rxjs';

import {
    ProjectModel
} from '../../../profile/models/project';

import {
    CategoryModel
} from '../../../profile/models/category';

@Component({

    selector: 'app-worklog-toolbar',

    standalone: true,

    imports: [

        CommonModule,

        ReactiveFormsModule

    ],

    templateUrl: './worklog-toolbar.html',

    styleUrl: './worklog-toolbar.scss'

})
export class WorkLogToolbar
implements OnInit {

    @Input()

    projects: ProjectModel[] = [];

    @Input()

    categories: CategoryModel[] = [];

    @Input()

    weekLabel = '';

    @Output()

    search =
    new EventEmitter<string>();

    @Output()

    projectChange =
    new EventEmitter<number | null>();

    @Output()

    categoryChange =
    new EventEmitter<number | null>();

    @Output()

    previousWeek =
    new EventEmitter<void>();

    @Output()

    nextWeek =
    new EventEmitter<void>();

    @Output()

    create =
    new EventEmitter<void>();

    private fb =
    inject(FormBuilder);

    toolbarForm =
    this.fb.group({

        search:[''],

        project_id:[null],

        category_id:[null]

    });

    ngOnInit(): void {

        this.toolbarForm.controls.search.valueChanges

            .pipe(

                debounceTime(300),

                distinctUntilChanged()

            )

            .subscribe(value=>{

                this.search.emit(
                    value ?? ''
                );

            });

        this.toolbarForm.controls.project_id.valueChanges

            .subscribe(value=>{

                this.projectChange.emit(value);

            });

        this.toolbarForm.controls.category_id.valueChanges

            .subscribe(value=>{

                this.categoryChange.emit(value);

            });

    }

}
