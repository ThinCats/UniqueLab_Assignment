## Introduction

域名系统（英文：Domain Name System，缩写：DNS）是互联网的一项服务。它作为将域名和IP地址相互映射的一个分布式数据库，能够使人更方便地访问互联网。DNS使用TCP和UDP端口53。当前，对于每一级域名长度的限制是63个字符，域名总长度则不能超过253个字符。
（因为偷懒，以上的假Introduction来自Wikipedia）

## Tasks

本期任务要求你使用任意一门你喜欢的语言（但是并不建议使用C/C++），实现一个**简单的**DNS服务器，要求手写DNS 报文。
However，**禁止任何形式的抄袭**。

## Basic Requirements

深入了解相关知识，使自己的DNS服务器支持UDP的DNS查询。

## Advanced Topics

1. 支持并发的DNS查询，并做可能的优化。
2. 实现较好的DNS缓存。
3. 同时支持UDP和TCP的DNS查询。

## Due Date && Deadline

Due Date: 5.20
Deadline: 5.27