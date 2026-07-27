export interface WorkLogListRequest {

    search: string;

    project_id: number | null;

    category_id: number | null;

    week: string;

    delete_status: boolean;

}
