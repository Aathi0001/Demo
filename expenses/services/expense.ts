import {
    Injectable,
    inject
} from '@angular/core';

import {
    HttpClient
} from '@angular/common/http';

import {
    Observable
} from 'rxjs';

import {
    API_ENDPOINTS
} from '../../../core/constants/api-endpoints';

import {
    ApiResponse
} from '../../../core/models/api-response';

import {
    ExpenseModel
} from '../models/expense';

import {
    ExpenseListRequest
} from '../models/expense-list-request';

import {
    ExpenseListResponse
} from '../models/expense-list-response';

import {
    CreateExpenseRequest
} from '../models/create-expense-request';

import {
    UpdateExpenseRequest
} from '../models/update-expense-request';

@Injectable({

    providedIn:'root'

})
export class ExpenseService {

    private http =
    inject(HttpClient);

    list(
        request:ExpenseListRequest
    ):Observable<ApiResponse<ExpenseListResponse>>{

        return this.http.post<ApiResponse<ExpenseListResponse>>(

            API_ENDPOINTS.EXPENSE_LIST,

            request

        );

    }

    detail(
        expenseId:number
    ):Observable<ApiResponse<ExpenseModel>>{

        return this.http.get<ApiResponse<ExpenseModel>>(

            API_ENDPOINTS.EXPENSE_DETAIL(
                expenseId
            )

        );

    }

    create(
        request:CreateExpenseRequest
    ):Observable<ApiResponse<any>>{

        return this.http.post<ApiResponse<any>>(

            API_ENDPOINTS.EXPENSE_CREATE,

            request

        );

    }

    update(

        expenseId:number,

        request:UpdateExpenseRequest

    ):Observable<ApiResponse<any>>{

        return this.http.put<ApiResponse<any>>(

            API_ENDPOINTS.EXPENSE_UPDATE(
                expenseId
            ),

            request

        );

    }

    scheduleDelete(
        expenseId:number
    ):Observable<ApiResponse<any>>{

        return this.http.post<ApiResponse<any>>(

            API_ENDPOINTS.EXPENSE_DELETE(
                expenseId
            ),

            {}

        );

    }

    restore(
        expenseId:number
    ):Observable<ApiResponse<any>>{

        return this.http.post<ApiResponse<any>>(

            API_ENDPOINTS.EXPENSE_RESTORE(
                expenseId
            ),

            {}

        );

    }

    permanentDelete(

        expenseId:number,

        request:{
            delete_password:string;
        }

    ):Observable<ApiResponse<any>>{

        return this.http.post<ApiResponse<any>>(

            API_ENDPOINTS.EXPENSE_PERMANENT_DELETE(
                expenseId
            ),

            request

        );

    }

}
