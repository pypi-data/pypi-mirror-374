# aliros

![license](https://img.shields.io/github/license/garrett-he/aliros)
![test](https://img.shields.io/github/actions/workflow/status/garrett-he/aliros/test.yml)
![version](https://img.shields.io/pypi/v/aliros)
![python](https://img.shields.io/pypi/pyversions/aliros)
![downloads](https://img.shields.io/pypi/dm/aliros)

A command-line tool to organize resources by [Resource Orchestration Service][1]
for [Alibaba Cloud][2].

## Usage

```
Usage: aliros [OPTIONS] COMMAND [ARGS]...

  A command-line tool to organize resources by Resource Orchestration Service
  for Alibaba Cloud.

Options:
  --version       Show version information.
  --region TEXT   Target region to use
  --profile TEXT  Name of profile to use
  --help          Show this message and exit.

Commands:
  abandon-stack                   Abandon the specified stack.
  create-stack                    Create a new stack.
  delete-stack                    Delete the specified stack.
  describe-resource-type          Describe resource type.
  describe-resource-type-template Describe resource type template.
  describe-stack                  Describe the specified stack.
  describe-stack-resource         Describe the specified resource in stack.
  describe-stack-template         Describe template of the specified stack.
  list-regions                    List available regions.
  list-resource-types             List available resource types.
  list-stack-events               List events of the specified stack.
  list-stack-resources            List resources of the specified stack.
  list-stacks                     List stacks.
  preview-stack                   Preview of creating stack.
  update-stack                    Update the specified stack.
  validate-template               Validate the specified template.

```

## License

Copyright (C) 2024 Garrett HE <garrett.he@outlook.com>

The BSD 3-Clause License, see [LICENSE](./LICENSE).

[1]: https://www.alibabacloud.com/help/doc-detail/28852.html

[2]: https://www.alibabacloud.com
