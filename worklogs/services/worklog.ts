import { inject, Injectable } from '@angular/core';

import { HttpClient } from '@angular/common/http';

import { Observable } from 'rxjs';

import { API } from '../../../core/constants/api.constants';

import { ApiResponse } from '../../../core/models/api-response';

import { WorkLogModel } from '../models/worklog';

import { WorkLogListRequest } from '../models/worklog-list-request';

import { WorkLogListResponse } from '../models/worklog-list-response';

import { CreateWorkLogRequest } from '../models/create-worklog-request';

import { UpdateWorkLogRequest } from '../models/update-worklog-request';

@Injectable({
    providedIn: 'root'
})
export class WorkLogService {

    private http =
        inject(HttpClient);

    list(
        request: WorkLogListRequest
    ): Observable<ApiResponse<WorkLogListResponse>> {

        return this.http.post<ApiResponse<WorkLogListResponse>>(
            API.WORKLOG.LIST,
            request
        );

    }

    detail(
        worklogId: number
    ): Observable<ApiResponse<WorkLogModel>> {

        return this.http.get<ApiResponse<WorkLogModel>>(
            `${API.WORKLOG.DETAIL}${worklogId}/`
        );

    }

    create(
        request: CreateWorkLogRequest
    ): Observable<ApiResponse<null>> {

        return this.http.post<ApiResponse<null>>(
            API.WORKLOG.CREATE,
            request
        );

    }

    update(
        worklogId: number,
        request: UpdateWorkLogRequest
    ): Observable<ApiResponse<null>> {

        return this.http.put<ApiResponse<null>>(
            `${API.WORKLOG.UPDATE}${worklogId}/`,
            request
        );

    }

    scheduleDelete(
        worklogId: number
    ): Observable<ApiResponse<null>> {

        return this.http.patch<ApiResponse<null>>(
            `${API.WORKLOG.SCHEDULE_DELETE}${worklogId}/`,
            {}
        );

    }

    restore(
        worklogId: number
    ): Observable<ApiResponse<null>> {

        return this.http.patch<ApiResponse<null>>(
            `${API.WORKLOG.RESTORE}${worklogId}/`,
            {}
        );

    }

    permanentDelete(
        worklogId: number,
        request: {
            delete_password: string;
        }
    ): Observable<ApiResponse<null>> {

        return this.http.delete<ApiResponse<null>>(
            `${API.WORKLOG.PERMANENT_DELETE}${worklogId}/`,
            {
                body: request
            }
        );

    }

}
