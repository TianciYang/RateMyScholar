from flask import Blueprint,jsonify,request,session
from . import db,professor_table,rating_professor_table,user_table,university_table,department_table
import os,binascii
import time
from user import verify_auth_token

professor = Blueprint('professor',__name__,url_prefix='/professor')

@professor.route('/',methods=["GET"])
def getprofessorInfo():
    try:
        data = db.session.query(professor_table).all()
        res = []
        for i in data:
            university_name = db.session.query(university_table).filter_by(uid=i.uid).first().name
            department_name = db.session.query(department_table).filter_by(did=i.did).first().name
            content = {'pid':i.pid,'uid':i.uid,'university':university_name,'did':i.did,'department':department_name,'name':i.name,'info':i.info}
            res.append(content)
        return jsonify({'msg':"success",'professor':res})
    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify({'msg':'error'})
@professor.route('/reviews/<pid>',methods=["GET","POST"])
def professorReviews(pid):
    if request.method == "POST":
        newReview = request.get_json()
        token = newReview.get('token')
        if token is None or verify_auth_token(token) is None:
            return jsonify(msg="invalid or expired token")

        rpid = binascii.b2a_hex(os.urandom(15))
        uuid = newReview.get("uuid")
        try:
            data = db.session.query(rating_professor_table).filter_by(uuid=uuid,pid=pid).all()
            if data != []:
                return jsonify({'msg':"error, already rated"})
            else:
                date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                review = rating_professor_table(rpid=rpid,uuid=uuid,pid=pid,score=newReview.get("score"),comment=newReview.get("comment"),num_agree=0,num_disagree=0,date=date)
                db.session.add(review)
                db.session.commit()
                return jsonify(msg="success")
        except Exception as e:
            print(e)
            db.session.rollback()
            return jsonify({'msg': "error"})
    else:
        try:
            data = db.session.query(rating_professor_table).filter_by(pid=pid).all()
            res = []
            for i in data:
                uuid = i.uuid
                j = db.session.query(user_table).filter_by(uuid=uuid).first()
                username = j.username
                content = {'rpid':i.rpid,'username':username,'pid':i.pid,'score':i.score,'comment':i.comment,'num_agree':i.num_agree,'num_disagree':i.num_disagree,'date':i.date}
                res.append(content)
            return jsonify({'msg':"success",'reviews':res})
        except Exception as e:
            print(e)
            db.session.rollback()
            return jsonify({'msg': 'error'})