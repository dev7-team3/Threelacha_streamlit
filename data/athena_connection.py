"""Athena 데이터베이스 연결 모듈"""

import os
import time
from typing import Optional

import boto3
import pandas as pd
import streamlit as st
from botocore.exceptions import ClientError, NoCredentialsError

from data.connection import DatabaseConnection


class AthenaConnection(DatabaseConnection):
    """Athena 데이터베이스 연결 클래스"""

    def __init__(self):
        self._client = None
        self._database = os.getenv("ATHENA_DATABASE", "team3_gold")
        self._workgroup = os.getenv("ATHENA_WORKGROUP", "team3-wg")
        self._output_location = os.getenv(
            "ATHENA_OUTPUT_LOCATION",
            "s3://team3-batch/gold/athena-results/",
        )

    def get_config(self) -> tuple[str, str]:
        """Athena 설정을 반환합니다.

        Returns:
            tuple[str, str]: database, workgroup
        """
        return self._database, self._workgroup

    def _get_client(self):
        """Athena 클라이언트를 생성하고 캐시합니다."""
        if self._client is None:
            region = os.getenv("AWS_REGION", "ap-northeast-2")
            config = {"region_name": region}

            access_key = os.getenv("AWS_ACCESS_KEY_ID")
            secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")

            if access_key and secret_key:
                config["aws_access_key_id"] = access_key
                config["aws_secret_access_key"] = secret_key

            try:
                self._client = boto3.client("athena", **config)
            except (NoCredentialsError, ClientError) as e:
                error_msg = f"Athena 연결 실패: {e!s}"
                st.error(error_msg)
                raise

        return self._client

    def execute_query(
        self,
        query: str,
        database: Optional[str] = None,
        workgroup: Optional[str] = None,
        output_location: Optional[str] = None,
        **kwargs,
    ) -> pd.DataFrame:
        """Athena 쿼리를 실행하고 DataFrame으로 반환합니다.

        Args:
            query: 실행할 SQL 쿼리 문자열
            database: Athena 데이터베이스 (기본값: 환경 변수 또는 team3_gold)
            workgroup: Athena WorkGroup (기본값: 환경 변수 또는 team3-wg)
            output_location: S3 출력 위치 (기본값: 환경 변수)
            **kwargs: 추가 파라미터 (호환성을 위해 유지)

        Returns:
            pd.DataFrame: 쿼리 결과를 담은 DataFrame
        """
        database = database or self._database
        workgroup = workgroup or self._workgroup
        output_location = output_location or self._output_location

        client = self._get_client()

        try:
            # 쿼리 실행 시작
            response = client.start_query_execution(
                QueryString=query,
                QueryExecutionContext={"Database": database},
                WorkGroup=workgroup,
                ResultConfiguration={"OutputLocation": output_location},
            )

            query_execution_id = response["QueryExecutionId"]

            # 쿼리 완료 대기
            while True:
                response = client.get_query_execution(
                    QueryExecutionId=query_execution_id
                )
                status = response["QueryExecution"]["Status"]["State"]

                if status in ["SUCCEEDED", "FAILED", "CANCELLED"]:
                    break

                time.sleep(1)

            if status == "FAILED":
                reason = response["QueryExecution"]["Status"].get(
                    "StateChangeReason", "Unknown error"
                )
                raise Exception(f"Athena 쿼리 실패: {reason}")

            if status == "CANCELLED":
                raise Exception("Athena 쿼리가 취소되었습니다.")

            # 결과 가져오기
            results = client.get_query_results(QueryExecutionId=query_execution_id)

            # 첫 번째 행은 컬럼명
            columns = [
                col["Name"]
                for col in results["ResultSet"]["ResultSetMetadata"]["ColumnInfo"]
            ]

            # 데이터 행 추출 (첫 번째 행 제외)
            rows = []
            for row in results["ResultSet"]["Rows"][1:]:
                row_data = []
                for col in row["Data"]:
                    value = col.get("VarCharValue", "")
                    # 숫자 타입 변환 시도
                    try:
                        if "." in value:
                            row_data.append(float(value))
                        else:
                            row_data.append(int(value))
                    except (ValueError, TypeError):
                        row_data.append(value)
                rows.append(row_data)

            # DataFrame 생성
            df = pd.DataFrame(rows, columns=columns)

            # 다음 페이지가 있으면 계속 가져오기
            next_token = results.get("NextToken")
            while next_token:
                results = client.get_query_results(
                    QueryExecutionId=query_execution_id,
                    NextToken=next_token,
                )

                for row in results["ResultSet"]["Rows"]:
                    row_data = []
                    for col in row["Data"]:
                        value = col.get("VarCharValue", "")
                        try:
                            if "." in value:
                                row_data.append(float(value))
                            else:
                                row_data.append(int(value))
                        except (ValueError, TypeError):
                            row_data.append(value)
                    rows.append(row_data)

                next_token = results.get("NextToken")

            # 최종 DataFrame 재생성 (모든 데이터 수집 후)
            df = pd.DataFrame(rows, columns=columns)
            return df

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            error_message = e.response.get("Error", {}).get("Message", f"{e!s}")
            raise Exception(
                f"Athena 클라이언트 오류 ({error_code}): {error_message}"
            ) from e
        except Exception as e:
            raise Exception(f"Athena 쿼리 실행 중 오류: {e!s}") from e
