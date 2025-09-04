#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import os

from datahub.utils import type_assert
from fastmcp import FastMCP

from datahub.core import DataHub
from datahub.models import BlobRecord

mcp = FastMCP("AliyunDatahubService")

access_id = os.getenv("ALIBABA_CLOUD_ACCESS_KEY_ID")
access_key = os.getenv("ALIBABA_CLOUD_ACCESS_KEY_SECRET")
endpoint = "https://dh-{}.aliyuncs.com"


def init_client(region="cn-hangzhou") -> DataHub:
    return DataHub(access_id=access_id, access_key=access_key, endpoint=endpoint.format(region))


# --------------------  datahub list api  --------------------

@mcp.tool()
def list_projects(region):
    dh = init_client(region)
    return dh.list_project()


@mcp.tool()
def list_topics(region, project_name):
    dh = init_client(region)
    return dh.list_topic(project_name)


@mcp.tool()
def list_connectors(region, project_name, topic_name):
    dh = init_client(region)
    return dh.list_connector(project_name, topic_name)


@mcp.tool()
def list_subscriptions(region, project_name, topic_name, query_key, page_index, page_size):
    dh = init_client(region)
    return dh.list_subscription(project_name, topic_name, query_key, page_index, page_size)


@mcp.tool()
def list_shards(region, project_name, topic_name):
    dh = init_client(region)
    return dh.list_shard(project_name, topic_name)


# --------------------  datahub get api  --------------------

@mcp.tool()
def get_project(region, project_name):
    dh = init_client(region)
    return dh.get_project(project_name)


@mcp.tool()
def get_topic(region, project_name, topic_name):
    dh = init_client(region)
    return dh.get_topic(project_name, topic_name)


@mcp.tool()
def get_connector(region, project_name, topic_name, connector_id):
    dh = init_client(region)
    return dh.get_connector(project_name, topic_name, connector_id)


@mcp.tool()
def get_subscription(region, project_name, topic_name, subscription_id):
    dh = init_client(region)
    return dh.get_subscription(project_name, topic_name, subscription_id)


# --------------------  datahub create api  --------------------

@mcp.tool()
def create_project(region, project_name, comment):
    dh = init_client(region)
    return dh.create_project(project_name, comment)


@mcp.tool()
def create_tuple_topic(region, project_name, topic_name, shard_count, life_cycle, record_schema, comment, extend_mode):
    dh = init_client(region)
    return dh.create_tuple_topic(project_name, topic_name, shard_count, life_cycle, record_schema, comment, extend_mode)


@mcp.tool()
def create_blob_topic(region, project_name, topic_name, shard_count, life_cycle, comment, extend_mode):
    dh = init_client(region)
    return dh.create_blob_topic(project_name, topic_name, shard_count, life_cycle, comment, extend_mode)


@mcp.tool()
def create_connector(region, project_name, topic_name, connector_type, column_fields, config, start_time):
    dh = init_client(region)
    return dh.create_connector(project_name, topic_name, connector_type, column_fields, config, start_time)


@mcp.tool()
def create_subscription(region, project_name, topic_name, comment):
    dh = init_client(region)
    return dh.create_subscription(project_name, topic_name, comment)


# --------------------  datahub delete api  --------------------

@mcp.tool()
def delete_project(region, project_name):
    dh = init_client(region)
    return dh.delete_project(project_name)


@mcp.tool()
def delete_topic(region, project_name, topic_name):
    dh = init_client(region)
    return dh.delete_topic(project_name, topic_name)


@mcp.tool()
def delete_connector(region, project_name, topic_name, connector_id):
    dh = init_client(region)
    return dh.delete_connector(project_name, topic_name, connector_id)


@mcp.tool()
def delete_subscription(region, project_name, topic_name, subscription_id):
    dh = init_client(region)
    return dh.delete_subscription(project_name, topic_name, subscription_id)


# --------------------  datahub pub/sub api  --------------------


@mcp.tool()
@type_assert(str, str, str, str)
def put_record_to_blob(region, project_name, topic_name, data):
    dh = init_client(region)

    records = []
    record = BlobRecord(blob_data=data)
    records.append(record)
    return dh.put_records(project_name, topic_name, records)


@mcp.tool()
@type_assert(str, str, str, list)
def put_records_to_blob(region, project_name, topic_name, datas):
    dh = init_client(region)

    records = []
    for data in datas:
        record = BlobRecord(blob_data=data)
        records.append(record)
    return dh.put_records(project_name, topic_name, records)


@mcp.tool()
def get_record_from_blob(region, project_name, topic_name, shard_id, limit_num=10):
    dh = init_client(region)
    result = dh.get_blob_records(project_name, topic_name, shard_id, limit_num)
    return result


if __name__ == "__main__":
    mcp.run(transport="stdio")



