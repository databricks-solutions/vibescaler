/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class DefaultService {
    /**
     * Health
     * Health check endpoint.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static healthHealthGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/health',
        });
    }
    /**
     * Detailed Health
     * Detailed health check with database and connection info.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static detailedHealthHealthDetailedGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/health/detailed',
        });
    }
    /**
     * Test
     * Test endpoint.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static testTestGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/test',
        });
    }
    /**
     * Deployment Status
     * Return DB-independent deployment setup status for the frontend shell.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static deploymentStatusDeploymentStatusGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/deployment/status',
        });
    }
}
