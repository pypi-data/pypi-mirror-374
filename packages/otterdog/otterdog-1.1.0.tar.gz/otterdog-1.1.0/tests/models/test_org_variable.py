#  *******************************************************************************
#  Copyright (c) 2023-2025 Eclipse Foundation and others.
#  This program and the accompanying materials are made available
#  under the terms of the Eclipse Public License 2.0
#  which is available at http://www.eclipse.org/legal/epl-v20.html
#  SPDX-License-Identifier: EPL-2.0
#  *******************************************************************************

from collections.abc import Mapping
from typing import Any

from otterdog.jsonnet import JsonnetConfig
from otterdog.models import ModelObject
from otterdog.models.organization_variable import OrganizationVariable

from . import ModelTest


class OrganizationVariableTest(ModelTest):
    def create_model(self, data: Mapping[str, Any]) -> ModelObject:
        return OrganizationVariable.from_model_data(data)

    @property
    def template_function(self) -> str:
        return JsonnetConfig.create_org_variable

    @property
    def model_data(self):
        raise NotImplementedError

    @property
    def provider_data(self):
        raise NotImplementedError
