export interface WorkLogModel {

    worklog_id: number;

    project_id: number | null;

    category_id: number | null;

    project_name: string | null;

    category_name: string | null;

    title: string | null;

    notes: string;

    work_date: string;

    duration: string;

    delete_status: boolean;

    created_at: string;

    updated_at: string;

}
