import {
    Component,
    HostListener,
    OnInit,
    inject
} from '@angular/core';

import {
    CommonModule
} from '@angular/common';

import {
    ChangeDetectorRef
} from '@angular/core';

import {
    WorkLogToolbar
} from '../../components/worklog-toolbar/worklog-toolbar';

import {
    WorkLogList
} from '../../components/worklog-list/worklog-list';

import {
    WorkLogForm
} from '../../components/worklog-form/worklog-form';

import {
    DeletePassword
} from '../../../anime/components/delete-password/delete-password';

import {
    WorkLogService
} from '../../services/worklog';

import {
    ProfileService
} from '../../../profile/services/profile';

import {
    WorkLogModel
} from '../../models/worklog';

import {
    WorkLogRequest
} from '../../models/worklog-request';

import {
    CreateWorkLogRequest
} from '../../models/create-worklog-request';

import {
    ProjectModel
} from '../../../profile/models/project';

import {
    CategoryModel
} from '../../../profile/models/category';

@Component({

    selector:'app-worklog',

    standalone:true,

    imports:[

        CommonModule,

        WorkLogToolbar,

        WorkLogList,

        WorkLogForm,

        DeletePassword

    ],

    templateUrl:'./worklog.html',

    styleUrl:'./worklog.scss'

})
export class WorkLog
implements OnInit{

    private workLogService=
    inject(WorkLogService);

    private profileService=
    inject(ProfileService);

    private cdr=
    inject(ChangeDetectorRef);

    groups:any[]=[];

    projects:ProjectModel[]=[];

    categories:CategoryModel[]=[];

    selectedWorkLog:WorkLogModel|null=null;

    openedWorkLog:WorkLogModel|null=null;

    showForm=false;

    showMenu=false;

    showDeleteDialog=false;

    isEditMode=false;

    menuX=0;

    menuY=0;

    weekLabel='';

    request:WorkLogRequest={

        search:'',

        project_id:null,

        category_id:null,

        delete_status:false,

        week_offset:0

    };

    ngOnInit():void{

        setTimeout(()=>{

            this.loadProjects();

            this.loadCategories();

            this.loadWorkLogs();

        });

    }

    loadProjects():void{

        this.profileService
        .projectOptions()
        .subscribe({

            next:response=>{

                this.projects=
                response.data;

            }

        });

    }

    loadCategories():void{

        this.profileService
        .categoryOptions()
        .subscribe({

            next:response=>{

                this.categories=
                response.data;

            }

        });

    }

    loadWorkLogs():void{

        this.workLogService
        .list(this.request)
        .subscribe({

            next:response=>{

                this.groups=
                response.data.groups;

                this.weekLabel=
                response.data.week;

                this.cdr.detectChanges();

            }

        });

    }

    create():void{

        this.selectedWorkLog=null;

        this.isEditMode=false;

        this.showForm=true;

    }

    closeForm():void{

        this.showForm=false;

        this.selectedWorkLog=null;

    }

    save(
        value:CreateWorkLogRequest
    ):void{

        if(this.isEditMode){

            this.updateWorkLog(value);

        }
        else{

            this.createWorkLog(value);

        }

    }

    createWorkLog(
        value:CreateWorkLogRequest
    ):void{

        this.workLogService
        .create(value)
        .subscribe({

            next:()=>{

                this.closeForm();

                this.loadWorkLogs();

            }

        });

    }

    updateWorkLog(
        value:CreateWorkLogRequest
    ):void{

        if(!this.selectedWorkLog){

            return;

        }

        this.workLogService
        .update(

            this.selectedWorkLog.worklog_id,

            value

        )
        .subscribe({

            next:()=>{

                this.closeForm();

                this.loadWorkLogs();

            }

        });

    }

    search(
        value:string
    ):void{

        this.request.search=value;

        this.loadWorkLogs();

    }

    projectChanged(
        projectId:number|null
    ):void{

        this.request.project_id=projectId;

        this.loadWorkLogs();

    }

    categoryChanged(
        categoryId:number|null
    ):void{

        this.request.category_id=categoryId;

        this.loadWorkLogs();

    }

    previousWeek():void{

        this.request.week_offset--;

        this.loadWorkLogs();

    }

    nextWeek():void{

        this.request.week_offset++;

        this.loadWorkLogs();

    }


        openWorkLog(
        workLog: WorkLogModel
    ): void {

        this.openedWorkLog = {

            ...workLog

        };

    }

    closeWorkLog(): void {

        this.openedWorkLog = null;

    }

    editWorkLog(): void {

        if (!this.selectedWorkLog) {

            return;

        }

        this.workLogService
            .detail(this.selectedWorkLog.worklog_id)
            .subscribe({

                next: response => {

                    this.selectedWorkLog =
                        response.data;

                    this.isEditMode = true;

                    this.showForm = true;

                    this.closeMenu();

                    this.cdr.detectChanges();

                }

            });

    }

    openMenu(
        data: any
    ): void {

        data.event.preventDefault();

        this.selectedWorkLog =
            data.workLog;

        this.menuX =
            data.event.clientX;

        this.menuY =
            data.event.clientY;

        this.showMenu = true;

    }

    closeMenu(): void {

        this.showMenu = false;

    }

    deleteWorkLog(): void {

        if (!this.selectedWorkLog) {

            return;

        }

        this.workLogService
            .scheduleDelete(
                this.selectedWorkLog.worklog_id
            )
            .subscribe({

                next: () => {

                    this.closeMenu();

                    this.openedWorkLog = null;

                    this.loadWorkLogs();

                }

            });

    }

    restoreWorkLog(): void {

        if (!this.selectedWorkLog) {

            return;

        }

        this.workLogService
            .restore(
                this.selectedWorkLog.worklog_id
            )
            .subscribe({

                next: () => {

                    this.closeMenu();

                    this.loadWorkLogs();

                }

            });

    }

    openDeleteDialog(): void {

        this.showDeleteDialog = true;

        this.closeMenu();

    }

    closeDeleteDialog(): void {

        this.showDeleteDialog = false;

    }

    permanentDelete(
        password: string
    ): void {

        if (!this.selectedWorkLog) {

            return;

        }

        this.workLogService
            .permanentDelete(

                this.selectedWorkLog.worklog_id,

                {

                    delete_password: password

                }

            )
            .subscribe({

                next: () => {

                    this.closeDeleteDialog();

                    this.closeMenu();

                    this.openedWorkLog = null;

                    this.loadWorkLogs();

                }

            });

    }

    @HostListener(
        'document:click',
        ['$event']
    )
    closeContextMenu(
        event: MouseEvent
    ): void {

        const target =
            event.target as HTMLElement;

        if (

            target.closest('.worklog-menu') ||

            target.closest('.menu-btn')

        ) {

            return;

        }

        this.showMenu = false;

    }

}
