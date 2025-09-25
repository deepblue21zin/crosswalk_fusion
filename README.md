# crosswalk_fusion
radar_project
(전체적인 구조)
로컬                    git hub(main)
  브랜치  <-------------> 브랜치

1) 작업 브랜치 만들기
  로컬에서 파일을 이미 수정한 상태여도, 새브랜치를 만들면 그 변경이 그대로 따라온다
  => git switch -c feat/<작업이름>
2)변경 파일 스테이징 -> 커밋
  => git add <수정한 파일>
  => git commit -m "feat(parser): 뭘 수정했는 지 간단히 설명"
3) 깃허브(원격)으로 푸시
   => git push -u origin feat/<작업이름>
   이 명령으로 GitHub에 동일 이름의 branch가 생성됨
4)Pull Request만들기(웹)
  GitHub 저장소로 이동 -> Compare&pull request버튼 클릭
      - base : main
      - compare: feat/<작업이름>
      - 제목/설명 작성 -> Create pull request -> 침원 리뷰/승인 -> Merge
5) 로컬 최신화&정리
   => git switch main
   => git pull origin main
6) branch 삭제
   => git branch -d feat/<작업이름>

//상황별 해결
- 원격이 먼저 업데이트되어 충돌 경고
- => git fetch origin
- => git rebase origin/main
- 실수로 main에서 커밋 했는데 아직 push안함
- => git switch -c feat/<작업이름>
- => git push -u origin feat/<작업이름>
- => git switch main
- => git reset --hard origin/main

- 
************
- 수정작업이 끝나고 push하고 반영이 되면 branch는 삭제해야함(즉 수정하고 바로 올리고 이걸 짧게 해야한다는 뜻)
- 커밋이라는 것은 현재 브랜치에 추가되는것
- 로컬 최신화는 누군가 수정하고 반영이되면 각자 해줘야 각자 반영된다. 즉 오늘 뭘 수정할려고 한다하면 최신화를 먼저 하고 -> 수정하고 -> 그걸 push해라
- git switch main
  git pull origin main
- 다른 팀원이 수정을 해서 내가 push할때 충돌이 나는경우, fetch origin을 해도 내것을 덮어 씌우는게 아니다.

![Uploading image.png…]()
A. “파일 하나 수정 → 팀과 공유(깃허브 반영)”

작업 브랜치 생성/전환

git switch -c feat/<작업명>   # main에서 시작


스테이징 → 커밋

git add <수정파일>
git commit -m "feat(scope): 메시지"


원격(깃허브)로 푸시

git push -u origin feat/<작업명>


PR 생성 → 리뷰 → Merge

모두 로컬 최신화

git switch main
git pull origin main
