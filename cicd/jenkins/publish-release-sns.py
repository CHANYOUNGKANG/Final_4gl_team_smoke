#!/usr/bin/env python3
"""Publish a bounded, non-secret release notification using the Jenkins EC2 role."""
import os
import re
import subprocess
import sys

LABELS = {
    "SMTP_RELAY_TEST": "시험 알림 (실제 배포 없음)",
    "SWITCH_VERIFIED": "정적시험 전환 성공 (Green)",
    "SYNTHETIC_ROLLBACK_VERIFIED": "정적시험 합성 롤백 성공 (Blue)",
    "ROLLBACK_VERIFIED": "전환 실패 / Blue 복귀 확인",
    "ROLLBACK_UNCONFIRMED": "복귀 미확인 / 즉시 확인",
    "NOT_CONFIRMED": "실패 또는 중단 / 전환·복귀 미확인",
}

def build_message(env, outcome):
    if outcome not in LABELS:
        raise ValueError("unsupported outcome")
    topic = env.get("SMOKE_DEPLOY_SNS_TOPIC_ARN", "")
    if not re.fullmatch(r"arn:aws:sns:ap-northeast-2:[0-9]{12}:[A-Za-z0-9_-]{1,256}", topic):
        raise ValueError("configure approved standard SNS topic in Jenkins")
    job = env.get("JOB_NAME", "")
    number = env.get("BUILD_NUMBER", "")
    if not re.fullmatch(r"[A-Za-z0-9_. /-]{1,160}", job) or not re.fullmatch(r"[0-9]{1,15}", number):
        raise ValueError("invalid job identity")
    commit = env.get("RELEASE_SOURCE_COMMIT", "")
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        commit = "unavailable"
    subject = "[배포] " + LABELS[outcome]
    body = "\n".join([
        subject,
        "결과: " + LABELS[outcome],
        "Job: " + job,
        "Build: " + number,
        "검증된 스크립트 커밋: " + commit,
        "Event ID: " + job + "#" + number + ":" + outcome,
        "수신 대상: smoke@smoke.local",
        "SNS 발행과 최종 메일 수신은 별도 검증 대상입니다.",
    ])
    return topic, subject, body

def publish(env, outcome):
    topic, subject, body = build_message(env, outcome)
    # No static keys or CLI debug output. No explicit retry of ambiguous publish.
    child_env = dict(env, AWS_MAX_ATTEMPTS="1", AWS_PAGER="")
    p = subprocess.run(
        ["aws", "sns", "publish", "--region", "ap-northeast-2",
         "--no-cli-pager", "--cli-connect-timeout", "5", "--cli-read-timeout", "10",
         "--topic-arn", topic, "--subject", subject, "--message", body,
         "--query", "MessageId", "--output", "text"],
        capture_output=True, text=True, timeout=25, env=child_env,
    )
    if p.returncode != 0 or not re.fullmatch(r"[0-9a-fA-F-]{36}", p.stdout.strip()):
        raise RuntimeError("SNS acceptance not confirmed")
    print("SNS PUBLISH ACCEPTED: MessageId=" + p.stdout.strip())

if __name__ == "__main__":
    try:
        if len(sys.argv) != 2:
            raise ValueError("one outcome required")
        publish(os.environ, sys.argv[1])
    except Exception as exc:
        print("SNS PUBLISH UNCONFIRMED: " + type(exc).__name__ + "; check private configuration, do not retry blindly", file=sys.stderr)
        sys.exit(1)
